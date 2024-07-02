import streamlit as st

st.title("Login")

def login():
    customer_email = st.text_input('Email')
    if st.button('Login'):
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer WHERE customer_email=%s", (customer_email,))
        customer = cursor.fetchone()
        if customer:
            st.session_state['customer_id'] = customer['customer_id']
            st.success("Logged in successfully")
            st.experimental_rerun()
