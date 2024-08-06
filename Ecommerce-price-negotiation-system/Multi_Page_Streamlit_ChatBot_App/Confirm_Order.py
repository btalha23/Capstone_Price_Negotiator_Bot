import streamlit as st
import mysql.connector


# MySQL Configuration
db_conn = None
if 'db_mysql' not in st.session_state:
    db_conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="price_negotiation"
    )
    st.session_state.db_mysql = db_conn

def confirm_order():
    if not st.session_state['cart']:
        st.experimental_set_query_params(page="Checkout")
        st.experimental_rerun()
        return

    customer_id = st.session_state.get('customer_id')
    if not customer_id:
        # st.write("Error: Customer is not logged in")
        st.switch_page(st.session_state['error_msg_page'])

    cart_items = st.session_state['cart']
    cursor = st.session_state.db_mysql.cursor()
    for item in cart_items:
        cursor.execute("""
            INSERT INTO CustomerInteractions (customer_id, product_id, interaction_type, quantity)
            VALUES (%s, %s, 'purchase', %s)
        """, (customer_id, item['product_id'], item['quantity']))
    st.session_state.db_mysql.commit()

    # Clear the cart after order confirmation
    st.session_state['cart'] = []
    st.write("Order confirmed! Thank you for your purchase.")

st.title("Confirm Order")

if st.session_state['customer_id']:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
else:
    st.sidebar.write("Not logged in")

confirm_order()

# def checkout():
#     st.title("Checkout")


            

        

