import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)

st.title("Welcome to the B2B Ecommerce Website!")
# st.sidebar.success("Select a page above.")

# home_page = st.Page("Homepage.py", title="Welcome to the B2B Ecommerce Website!")
login_page = st.Page("Login.py", title="Login")
products_page = st.Page("Products.py", title="Products")
register_customer_page = st.Page("Register.py", title="Register")
price_negotiation_chatbot_page = st.Page("Price_Negotiation.py", title="Price Negotiator Bot")
checkout_page = st.Page("Checkout.py", title="Checkout")

pg = st.navigation([login_page, 
                    products_page, 
                    register_customer_page, 
                    price_negotiation_chatbot_page,
                    checkout_page])
pg.run()


