import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

st.title("Price Negotiator Chatbot")

load_dotenv(find_dotenv())

def get_sql_chain(db):
    template = """
        You are a sales representative at a company. You are interacting with a user who is asking you 
        to reduce the price of products in the shopping cart.

        Based on the table schema below, write a SQL query that would answer the user's question. 
        Take the conversation history into account.

        <SCHEMA>{schema}</SCHEMA>

        Conversation History: {chat_history}

        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, 
        not even backticks.

        For example:
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
        | llm
        | StrOutputParser()
    )

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    
    template = """
        You are a sales representative at a company. You are interacting with a user who is asking you 
        questions about the products in their shopping cart. Follow these guidelines during the interaction:

        1. Do not offer a discount unless the customer explicitly asks for a price reduction.
           If the customer is asking for the price or other product details without mentioning a discount, 
           provide an exact answer without offering a discount.
        2. If the customer asks for a discount, do not disclose the maximum possible discount based 
           on the product price margin percentage in the first interaction.
           Offer a small discount incrementally.
        3. If there are more multiple prices of the same product in the product catelogue, 
           always use the maximum price in customer engagement.
        4. Engage in a bargaining conversation if the customer asks for further reductions.
           Increase the discount in small steps and always wait for the customer's response before 
           making further offers.
        5. If the customer is satisfied with a price and does not ask for more discounts, 
           do not offer additional discounts. Lock the price that is acceptable for the customer.
        6. Always respond with understanding and empathy.
           Avoid giving detailed explanations for the discounts and focus on maintaining a friendly 
           and helpful tone.

        Based on the table schema below, question, sql query, sql response, and example response
        write a natural language response.
        
        <SCHEMA>{schema}</SCHEMA>

        Examples of past interactions:
        
        Conversation History: {chat_history}

        Example 1:
        User Question: What is the price of the Premium Frying Pan?
        SQL Query: SELECT MAX(product_price) 
                   FROM product 
                   WHERE product_name = 'frying pan';
        SQL Response: 60.00
        Response: The price for the Premium Frying Pan is $60.00.
        
        Example 2:
        User Question: Can you give me a better price on the Deluxe Saucepan?
        SQL Query: SELECT MAX(product_price) 
                   FROM product 
                   WHERE product_name = 'saucepan';
        SQL Response: 50.00
        Response: The price for the Deluxe Saucepan is $50.00. I can offer you a small discount of $1.00. 
                   How does that sound?

        User Question: Can you do better than that?
        SQL Query: SELECT MAX(product_price * product_margin_percent / 100) * 0.25 AS medium_discount FROM product WHERE product_name = 'saucepan';
        SQL Response: 2.50
        Response: I understand you want a better deal. I can increase the discount to $2.50. 
                   Does this work for you?

        User Question: I am interested to ask for an even lower price?
        SQL Query: SELECT MAX(product_price * product_margin_percent / 100) * 0.5 AS fifty_percent_discount FROM product WHERE product_name = 'saucepan';
        SQL Response: 5.0
        Response: It is good to see your interest in the product. Based on your interest I can take off $5.0 
                  from the original price. Is it okay?

        User Question: I was hoping for a bit more.
        SQL Query: SELECT MAX(product_price * product_margin_percent / 100) * 0.75 AS large_discount 
                   FROM product 
                   WHERE product_name = 'saucepan';
        SQL Response: 7.50
        Response: You're driving a hard bargain! How about $7.50 off? This is my best offer.

        Example 3:
        User Question: I'm looking to get a discount on the Premium Frying Pan.
        SQL Query: SELECT MAX(product_price) 
                   FROM product 
                   WHERE product_name = 'frying pan';
        SQL Response: 60.00
        Response: The price for the Premium Frying Pan is $60.00. I can offer you a $1.20 discount. 
                   What do you think?

        User Question: Can you lower the price a bit more?
        SQL Query: SELECT MAX(product_price * product_margin_percent / 100) * 0.25 AS medium_discount 
                   FROM product 
                   WHERE product_name = 'frying pan';
        SQL Response: 3.00
        Response: I can stretch it a bit further and offer you $3.00 off. Does that sound good?

        User Question: I am interested to ask for an even lower price?
        SQL Query: SELECT MAX(product_price * product_margin_percent / 100) * 0.5 AS fifty_percent_discount FROM product WHERE product_name = 'saucepan';
        SQL Response: 6.75
        Response: It is good to see your interest in the product. Based on your interest I can take off $6.75 
                  from the original price. Is it okay?

        User Question: I'm still looking for a better deal.
        SQL Query: SELECT MAX(product_price * product_margin_percent / 100) * 0.75 AS large_discount 
                   FROM product 
                   WHERE product_name = 'frying pan';
        SQL Response: 8,25
        Response: Alright, I can go up to $8.25 off. This is the final discount I can offer.

        Example 4:
        User Question: What is the price after the discount.
        SQL Query: SELECT
                        MAX(product_price), 
                        MAX(product_price * product_margin_percent / 100) * 0.08 AS large_discount,
                        MAX(product_price - (product_price * product_margin_percent / 100) * 0.08) AS final_price, 
                   FROM product 
                   WHERE product_name = 'frying pan';
        SQL Response: 55.20
        Response: The price after the discount is $55.20.


        Your turn:
        SQL Query: <SQL>{query}</SQL>
        User Question: {question}
        SQL Response: {response}
        Response: 
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
    AIMessage(content="Hello, I am a price negotiator bot. Lets start bargaining")
  ]

db = init_database(
  user="root",
  password="root",
  host="localhost",
  port="3306",
  database="price_negotiation"
)
st.session_state.db = db

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