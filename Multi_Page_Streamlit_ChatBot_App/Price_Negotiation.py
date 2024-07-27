import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv

loyalty_customer_eligibity = [{"loyalty_customer_num_purchase_days": 3},
                              {"loyalty_customer_bulk_purchases_quantity": 30},
                            ]

previous_response_lc = ""
previous_response_lc_bp = ""
previous_response_lc_pn = ""

# Initialization
if 'previous_response_lc' not in st.session_state:
    st.session_state['previous_response_lc'] = None

if 'previous_response_lc_bp' not in st.session_state:
    st.session_state['previous_response_lc_bp'] = None

if 'previous_response_lc_pn' not in st.session_state:
    st.session_state['previous_response_lc_pn'] = None

if 'loyalty_customer_eligibity_checked' not in st.session_state:
    st.session_state['loyalty_customer_eligibity_checked'] = False

if 'loyalty_customer_bulk_purchase_checked' not in st.session_state:
    st.session_state['loyalty_customer_bulk_purchase_checked'] = False

if 'loyalty_customer_price_negotiation' not in st.session_state:
    st.session_state['loyalty_customer_price_negotiation'] = False

if 'loyalty_customer_flag' not in st.session_state:
    st.session_state['loyalty_customer_flag'] = False

if 'lc_bulk_purchase_flag' not in st.session_state:
    st.session_state['lc_bulk_purchase_flag'] = False

if 'global_get_response_count' not in st.session_state:
    st.session_state['global_get_response_count'] = 0

def get_loyalty_customer_num_purchase_days(_):
    return loyalty_customer_eligibity[0]

def get_loyalty_customer_bulk_purchases_quantity(_):
    return loyalty_customer_eligibity[1]

# def get_customer_id(_):
#     print(f"session_state_customer_id {st.session_state.get('customer_id')}")
#     print(f"session_state_customer_id {st.session_state['customer_id']}")
#     # return st.session_state['customer_id']
#     return st.session_state.get('customer_id')

def get_sql_chain_loyalty_customer(db):
    template = """
        You are a sales representative at a company. You are interacting with customers to offer them special
        discounts. These discounts are subject to if the customer qualifies as a loyalty customer. 
        First of all check if the user is a valid logged in user. To verify this, evaluate {customer_id}. 
        If {customer_id} is empty or is None, then inform that the customer is not logged in.
        If {customer_id}  has a valid value, extract all records for the customer with customer ID 
        {customer_id}.

        To be a loyalty customer there should be a purchase record associated with the customer 
        for a minumun of {loyalty_customer_num_purchase_days} unique dates. If there are more than one purchase on a day, count that day only
        once.

        Based on the table schema below, write a SQL query that would answer the user's question. 
        Take the conversation history into account.

        <SCHEMA>{schema}</SCHEMA>

        Conversation History: {chat_history}

        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, 
        not even backticks.

        For example:
        Question: Check for being a loyalty customer
        SQL Query: SELECT customer_id, COUNT(DISTINCT DATE(interaction_date)) AS purchase_days
                    FROM CustomerInteractions
                    WHERE interaction_type = 'purchase' AND customer_id = {customer_id}
                    GROUP BY customer_id
                    HAVING purchase_days >= 10;
        Question: What is the average price of the saucepans?
        SQL Query: SELECT AVG(product_price) AS average_price FROM product WHERE product_name = 'Saucepan';
        Question: Name 10 products
        SQL Query: SELECT product_name FROM product LIMIT 10;

        Your turn:

        Question: {question}
        SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)
  
    llm = ChatOpenAI(temperature=0, 
                 model="gpt-3.5-turbo-0613")
    
    def get_schema(_):
        return db.get_table_info()
        
    return (
        RunnablePassthrough.assign(schema=get_schema).assign(
            loyalty_customer_num_purchase_days=get_loyalty_customer_num_purchase_days)
        | prompt
        | llm.bind(stop=["\nSQL Result:"])
        | StrOutputParser()
    )

def get_response_loyalty_customer(user_query: str, db: SQLDatabase, chat_history: list, customer_id: int):
    st.session_state['loyalty_customer_eligibity_checked'] = True

    sql_chain = get_sql_chain_loyalty_customer(db)

    print(f"customer_id: {customer_id}")

    template = """
        You are a sales representative at a company. You are interacting with customers to offer them special
        discounts. These discounts are subject to if the customer qualifies as a loyalty customer. 
        First of all check if the user is a valid logged in user. To verify this, evaluate {customer_id}. 
        If {customer_id} is empty or is None, then inform that the customer is not logged in.
        If {customer_id}  has a valid value, extract all records for the customer with customer ID 
        {customer_id}. 

        To be a loyalty customer there should be a purchase record associated with the customer 
        for a minumun of {loyalty_customer_num_purchase_days} unique dates. If there are more than one purchase on a day, count that day only
        once. 
        
        If the sql response is empty, then get the actual number of purchase days and inform 
        the customer that the customer is not eligible for the discount. 
        
        Based on the table schema below, question, sql query, and sql response, write a natural language response.
        The natural language response should not have any mention of SQL response and SQL query.

        <SCHEMA>{schema}</SCHEMA>
    
        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User Question: {question}
        SQL Response: {response}
        """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI(temperature=0, 
                    model="gpt-3.5-turbo-0613")  
    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
        schema=lambda _: db.get_table_info(),
        response=lambda vars: db.run(vars["query"]),
        loyalty_customer_num_purchase_days=get_loyalty_customer_num_purchase_days
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
        "customer_id": customer_id
    })

def get_sql_chain_lc_bulk_purchase(db):
    template = """
        You are a sales representative at a company. You are interacting with loyalty customers to offer them special
        discounts. These discounts are subject to if the loyalty customers purchase items in bulk on 
        the day of the purchase. Bulk means {loyalty_customer_bulk_purchases_quantity} or more units of a 
        particular product in one purchase on a single date. To be eligible for the discount the purchase 
        should have today's date. Any previous records of purchases of more than 
        {loyalty_customer_bulk_purchases_quantity} units of that particular product do not contribute 
        towards the discount today.

        Based on the table schema below, write a SQL query that would answer the user's question. 
        Take the conversation history into account.

        <SCHEMA>{schema}</SCHEMA>

        Conversation History: {chat_history}

        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, 
        not even backticks.

        For example:
        Question: Check for bulk purchase to determine the discount
        SQL Query: SELECT 
                        customer_id, 
                        product_id,
                        DATE(interaction_date) AS purchase_date,  
                        SUM(quantity) AS total_quantity
                   FROM 
                        CustomerInteractions
                   WHERE 
                        interaction_type = 'purchase'
                        AND DATE(interaction_date) = CURRENT_DATE
                   GROUP BY 
                        customer_id, 
                        product_id, 
                        DATE(interaction_date)
                   HAVING 
                        total_quantity >= 30;
        Question: Check for being a loyalty customer
        SQL Query: SELECT customer_id, COUNT(DISTINCT DATE(interaction_date)) AS purchase_days
                   FROM CustomerInteractions
                   WHERE interaction_type = 'purchase'
                   GROUP BY customer_id
                   HAVING purchase_days >= 10;
        Question: What is the average price of the saucepans?
        SQL Query: SELECT AVG(product_price) AS average_price FROM product WHERE product_name = 'Saucepan';
        Question: Name 10 products
        SQL Query: SELECT product_name FROM product LIMIT 10;

        Your turn:

        Question: {question}
        SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)
  
    llm = ChatOpenAI(temperature=0, 
                 model="gpt-3.5-turbo-0613")
    
    def get_schema(_):
        return db.get_table_info()
        
    return (
        RunnablePassthrough.assign(schema=get_schema).assign(
            loyalty_customer_bulk_purchases_quantity=get_loyalty_customer_bulk_purchases_quantity
        )
        | prompt
        | llm.bind(stop=["\nSQL Result:"])
        | StrOutputParser()
    )

def get_response_lc_bulk_purchase(user_query: str, db: SQLDatabase, chat_history: list):
    st.session_state['loyalty_customer_bulk_purchase_checked'] = True

    print("In the function for checking the bulk purchase")
    print(user_query)    
    sql_chain = get_sql_chain_lc_bulk_purchase(db)
    # print(sql_chain.invoke({"question": user_query, "chat_history": chat_history}))    
    # x=0
    # while (1):
    #     x = x + 1

    template = """
        You are a sales representative at a company. You are interacting with customers to offer them special
        discounts. These discounts are subject to if the loyalty customers purchase items in bulk on 
        the day of the purchase. Bulk means {loyalty_customer_bulk_purchases_quantity} or more units of a 
        particular product in one purchase on one day. To be eligible for the discount the purchase 
        should have today's date. Any previous records of purchase of more than 
        {loyalty_customer_bulk_purchases_quantity} units of a product do not contribute towards 
        the discount today. Get the actual names of the products for which the discount is available.
        If the sql response is empty, then inform the loyalty customer that the customer 
        is not eligible for the discount. 
        
        Based on the table schema below, question, sql query, and sql response, write a natural language response.
        The natural language response should not have any mention of SQL response and SQL query.

        <SCHEMA>{schema}</SCHEMA>
    
        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User Question: {question}
        SQL Response: {response}
        """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI(temperature=0, 
                    model="gpt-3.5-turbo-0613")  
    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
        schema=lambda _: db.get_table_info(),
        response=lambda vars: db.run(vars["query"]),
        loyalty_customer_bulk_purchases_quantity=get_loyalty_customer_bulk_purchases_quantity
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })

def get_sql_chain_lc_price_negotiation(db):
    template = """
        You are a sales representative at a company. You are interacting with loyalty customers to offer them special
        discounts. These discounts are subject to if the loyalty customers purchase items in bulk on 
        the day of the purchase. Bulk means {loyalty_customer_bulk_purchases_quantity} or more units of a 
        particular product in one purchase on a single date. To be eligible for the discount the purchase 
        should have today's date. Any previous records of purchases of more than 
        {loyalty_customer_bulk_purchases_quantity} units of that particular product do not contribute 
        towards the discount today.

        Based on the table schema below, write a SQL query that would answer the user's question. 
        Take the conversation history into account.

        <SCHEMA>{schema}</SCHEMA>

        Conversation History: {chat_history}

        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, 
        not even backticks.

        For example:
        Question: Check for bulk purchase to determine the discount
        SQL Query: SELECT 
                        customer_id, 
                        product_id,
                        DATE(interaction_date) AS purchase_date,  
                        SUM(quantity) AS total_quantity
                   FROM 
                        CustomerInteractions
                   WHERE 
                        interaction_type = 'purchase'
                        AND DATE(interaction_date) = CURRENT_DATE
                   GROUP BY 
                        customer_id, 
                        product_id, 
                        DATE(interaction_date)
                   HAVING 
                        total_quantity >= 30;
        Question: Check for being a loyalty customer
        SQL Query: SELECT customer_id, COUNT(DISTINCT DATE(interaction_date)) AS purchase_days
                   FROM CustomerInteractions
                   WHERE interaction_type = 'purchase'
                   GROUP BY customer_id
                   HAVING purchase_days >= 10;
        Question: What is the average price of the saucepans?
        SQL Query: SELECT AVG(product_price) AS average_price FROM product WHERE product_name = 'Saucepan';
        Question: Name 10 products
        SQL Query: SELECT product_name FROM product LIMIT 10;

        Your turn:

        Question: {question}
        SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)
  
    llm = ChatOpenAI(temperature=0, 
                 model="gpt-3.5-turbo-0613")
    
    def get_schema(_):
        return db.get_table_info()
        
    return (
        RunnablePassthrough.assign(schema=get_schema).assign(
            loyalty_customer_bulk_purchases_quantity=get_loyalty_customer_bulk_purchases_quantity
        )
        | prompt
        | llm.bind(stop=["\nSQL Result:"])
        | StrOutputParser()
    )

def get_response_lc_price_negotiation(user_query: str, db: SQLDatabase, chat_history: list):
    st.session_state['loyalty_customer_price_negotiation'] = True

    print("In the function for price negotiation")
    print(user_query)    
    sql_chain = get_sql_chain_lc_price_negotiation(db)
    # print(sql_chain.invoke({"question": user_query, "chat_history": chat_history}))    
    # x=0
    # while (1):
    #     x = x + 1

    template = """
        You are a sales representative at a company. You are interacting with customers to offer them special
        discounts. These discounts are subject to if the loyalty customers purchase items in bulk on 
        the day of the purchase. Bulk means {loyalty_customer_bulk_purchases_quantity} or more units of a 
        particular product in one purchase on one day. To be eligible for the discount the purchase 
        should have today's date. Any previous records of purchase of more than 
        {loyalty_customer_bulk_purchases_quantity} units of a product do not contribute towards 
        the discount today. Get the actual names of the products for which the discount is available.
        If the sql response is empty, then inform the loyalty customer that the customer 
        is not eligible for the discount. 
        
        Based on the table schema below, question, sql query, and sql response, write a natural language response.
        The natural language response should not have any mention of SQL response and SQL query.

        <SCHEMA>{schema}</SCHEMA>
    
        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User Question: {question}
        SQL Response: {response}
        """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI(temperature=0, 
                    model="gpt-3.5-turbo-0613")  
    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
        schema=lambda _: db.get_table_info(),
        response=lambda vars: db.run(vars["query"]),
        loyalty_customer_bulk_purchases_quantity=get_loyalty_customer_bulk_purchases_quantity
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })

def get_response(user_query: str, db: SQLDatabase, chat_history: list, customer_id: int):
    print(f"get_response count {st.session_state['global_get_response_count']}")
    
    print(f"loyalty customer check {st.session_state['loyalty_customer_eligibity_checked']}")
    # print(loyalty_customer_eligibity_checked)
    if not st.session_state['loyalty_customer_eligibity_checked']:
        print("Checking loyalty customer eligibility")
        response_loyalty_customer = \
            get_response_loyalty_customer(user_query, db, chat_history, customer_id)
        # global previous_response_lc
        final_response = st.session_state['previous_response_lc'] = response_loyalty_customer
        print(f"loyalty customer check {st.session_state['loyalty_customer_eligibity_checked']}")
        # print(loyalty_customer_eligibity_checked)

    if (st.session_state['global_get_response_count'] == 1) and st.session_state['loyalty_customer_eligibity_checked']:
        print("loyalty customer flag setup")
        previous_response_lc = st.session_state['previous_response_lc']
        print(f"previous_response_lc: {previous_response_lc}")
        print(f"the find response: {previous_response_lc.find('not')}")
        if previous_response_lc.find('not') != -1:
            print("The customer is not a loyalty customer")
            st.session_state['loyalty_customer_flag'] = False
        else:
            print("The customer is a loyalty customer")
            st.session_state['loyalty_customer_flag'] = True
    
    if st.session_state['loyalty_customer_flag'] and not st.session_state['loyalty_customer_bulk_purchase_checked']:
        print("Checking for the bulk purchase")
        response_bulk_purchase = \
            get_response_lc_bulk_purchase(user_query, db, chat_history)
        # global previous_response_lc_bp
        final_response = st.session_state['previous_response_lc_bp'] = response_bulk_purchase
        print(final_response)
    
    if (st.session_state['global_get_response_count'] == 2) and st.session_state['loyalty_customer_bulk_purchase_checked']:
        print("loyalty customer bulk purchase flag setup")
        previous_response_lc_bp = st.session_state['previous_response_lc_bp']
        print(f"previous_response_lc_bp: {previous_response_lc_bp}")
        if previous_response_lc_bp.find('not') != -1:
            print("The customer is not eligible for further discounts")
            st.session_state['lc_bulk_purchase_flag'] = False
        else:
            print("The customer is a loyalty customer")
            st.session_state['lc_bulk_purchase_flag'] = True

    if st.session_state['lc_bulk_purchase_flag'] and not st.session_state['loyalty_customer_price_negotiation']:
        print("Starting the price negotiation process")
        response_price_negotiation = \
            get_response_lc_price_negotiation(user_query, db, chat_history)
        global previous_response_lc_pn
        final_response = previous_response_lc_pn = response_price_negotiation
        print(final_response)

    if (st.session_state['global_get_response_count'] >= 3) and st.session_state['loyalty_customer_price_negotiation']:
        print("Price negotiation process in progress")
        response_price_negotiation = \
            get_response_lc_price_negotiation(user_query, db, chat_history)
        # global previous_response_lc_pn
        final_response = st.session_state['previous_response_lc_pn'] = response_price_negotiation
        print(final_response)

    if (st.session_state['global_get_response_count'] >= 1) and not st.session_state['loyalty_customer_flag']:
        final_response = st.session_state['previous_response_lc']

    st.session_state['global_get_response_count'] = st.session_state['global_get_response_count'] + 1
    print(f"get_response count {st.session_state['global_get_response_count']}")

    return final_response

st.title("Price Negotiator Chatbot")

load_dotenv(find_dotenv())

if st.session_state['customer_id']:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
else:
    st.sidebar.write("Not logged in")

print(f"session_state_customer_id {st.session_state['customer_id']}")

if "chat_history" not in st.session_state:
  st.session_state.chat_history = [
    AIMessage(content="""Hello, I am a price negotiator bot. 
              Loyalty customers are eligible for special offers. 
              Lets start evaluating your eligibilty.""")
  ]

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

last_ai_message = ""
user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        # response = get_response_loyalty_customer(user_query, st.session_state.db, st.session_state.chat_history)
        response = get_response(user_query, 
                                st.session_state.db, 
                                st.session_state.chat_history,
                                st.session_state.customer_id)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))