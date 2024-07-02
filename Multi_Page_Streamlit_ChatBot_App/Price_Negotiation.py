import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv

loyalty_customer_eligibity = {
    "LOYALTY_CUSTOMER_NUM_PURCHASES": 10,
    "LOYALTY_CUSTOMER_NUM_PURCHASE_DAYS": 10}

st.title("Price Negotiator Chatbot")

load_dotenv(find_dotenv())

def get_sql_chain(db):
    template = """
        You are a sales representative at a company. You are interacting with customers to offer them special
        discounts. These discounts are subject to if the customer qualifies as a loyalty customer. 
        To be a loyalty customer there should be a purchase record associated with the customer 
        for a minumun of 10 unique dates. If there are more than one purchase on a day, count that day only
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
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm.bind(stop=["\nSQL Result:"])
        | StrOutputParser()
    )

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    
    template = """
        You are a sales representative at a company. You are interacting with customers to offer them special
        discounts. These discounts are subject to if the customer qualifies as a loyalty customer. 
        To be a loyalty customer there should be a purchase record associated with the customer 
        for a minumun of 10 unique dates. If there are more than one purchase on a day, count that day only
        once. If the sql response is empty, then get the actual number of purchase days and inform 
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
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })

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

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))