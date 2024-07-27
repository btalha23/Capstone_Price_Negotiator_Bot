import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage

# Initialization
if 'home_page' not in st.session_state:
    st.session_state['home_page'] = False

if 'login_page' not in st.session_state:
    st.session_state['login_page'] = None

if 'products_page' not in st.session_state:
    st.session_state['products_page'] = None

if 'register_customer_page' not in st.session_state:
    st.session_state['register_customer_page'] = None

# if 'view_cart_page' not in st.session_state:
#     st.session_state['view_cart_page'] = None

if 'price_negotiation_chatbot_page' not in st.session_state:
    st.session_state['price_negotiation_chatbot_page'] = None

if 'checkout_page' not in st.session_state:
    st.session_state['checkout_page'] = None

if 'error_msg_page' not in st.session_state:
    st.session_state['error_msg_page'] = None

home_page = st.Page("Homepage.py", title="Multipage App", icon="👋")
login_page = st.Page("Login.py", title="Login")
register_customer_page = st.Page("Register.py", title="Register")
products_page = st.Page("Products.py", title="Products")
confirm_order_page = st.Page("Confirm_Order.py", title="Confirm Order")
price_negotiation_chatbot_page = st.Page("Price_Negotiation.py", title="Price Negotiator Bot")
checkout_page = st.Page("Checkout.py", title="Checkout")
error_msg_page = st.Page("Error_Msg.py", title="Error")

pg = st.navigation([home_page,
                    login_page, 
                    register_customer_page, 
                    products_page, 
                    checkout_page,
                    confirm_order_page, 
                    price_negotiation_chatbot_page,
                    error_msg_page])
pg.run()

st.session_state['home_page'] = home_page
st.session_state['login_page'] = login_page
st.session_state['register_customer_page'] = register_customer_page
st.session_state['price_negotiation_chatbot_page'] = price_negotiation_chatbot_page
st.session_state['checkout_page'] = checkout_page
st.session_state['confirm_order_page'] = confirm_order_page
st.session_state['error_msg_page'] = error_msg_page