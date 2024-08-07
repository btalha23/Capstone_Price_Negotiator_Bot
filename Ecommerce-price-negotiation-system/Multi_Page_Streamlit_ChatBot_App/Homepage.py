import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

# Initialize session state for cart and customer ID
if 'cart' not in st.session_state:
    st.session_state['cart'] = []
if 'customer_id' not in st.session_state:
    st.session_state['customer_id'] = None

print(f"session_state_customer_id {st.session_state['customer_id']}")

st.title("Welcome to the B2B Ecommerce Website!")
# st.sidebar.success("Select a page above.")

db = init_database(
  user="root",
  password="MyNewPass1!",
  host="localhost",
  port="3306",
  database="price_negotiation"
)
st.session_state.db = db

def restart_app():
  # Delete all the items in Session state
  for key in st.session_state.keys():
    del st.session_state[key]
  
  st.rerun()

if st.session_state['customer_id']:
        # st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.button("Logout", on_click=lambda: restart_app())
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
else:
    st.sidebar.write("Not logged in")
