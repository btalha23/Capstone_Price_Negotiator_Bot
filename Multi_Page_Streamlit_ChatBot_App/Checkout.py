import streamlit as st
import mysql.connector
# from streamlit_extras.switch_page_button import switch_page

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

# pg_checkout = st.navigation(pages=[st.session_state['confirm_order_page'], 
#                                    st.session_state['price_negotiation_chatbot_page'],
#                                   ],
#                             position="hidden")
# pg_checkout.run()

def checkout():
    if not st.session_state['cart']:
        st.write("Your cart is empty")
        return
    
    cursor = st.session_state.db_mysql.cursor(dictionary=True)
    cart_items = [item['product_id'] for item in st.session_state['cart']]
    placeholders = ', '.join(['%s'] * len(cart_items))
    query = f"SELECT * FROM Product WHERE product_id IN ({placeholders})"
    cursor.execute(query, cart_items)
    products = cursor.fetchall()

    # st.write("### Checkout")
    total_price = 0
    for item in st.session_state['cart']:
        for product in products:
            if product['product_id'] == item['product_id']:
                #st.image(f"./static/images/{product['product_image']}", width=150)
                st.write(product['product_name'])
                st.write(f"Price: ${product['product_price']}")
                st.write(f"Quantity: {item['quantity']}")
                st.write('---')
                total_price += product['product_price'] * item['quantity']
    
    st.write(f"Total Price: ${total_price}")

    if st.button('Confirm Order'):
        st.switch_page(st.session_state['confirm_order_page'])
        # switch_page(st.session_state['confirm_order_page'])

    if st.button('Start Price Negotiation'):
        st.switch_page(st.session_state['price_negotiation_chatbot_page'])

st.title("Checkout")

if st.session_state['customer_id']:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
else:
    st.sidebar.write("Not logged in")

checkout()

# if not st.session_state['cart']:
#     st.write("Your cart is empty")
# else:      
#     db_conn_2 = st.session_state.db
#     # cursor = st.session_state.db.cursor(dictionary=True)
#     cart_items = [item['product_id'] for item in st.session_state['cart']]
#     print(f"cart_items {cart_items}")
#     placeholders = ', '.join(['%s'] * len(cart_items))
#     print(f"placeholders {placeholders}")
#     query = f"SELECT * FROM Product WHERE product_id IN ({placeholders})"
#     print(f"query {query}")

#     # cursor.execute(query, cart_items)
#     # products = cursor.fetchall()
