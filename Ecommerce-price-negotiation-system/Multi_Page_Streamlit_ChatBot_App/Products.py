
st.title("Products")
import streamlit as st
import mysql.connector
import os
from io import BytesIO

# MySQL Configuration
db_conn = None
if 'db' not in st.session_state:
    db_conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="price_negotiation"
    )
    st.session_state.db = db_conn

# Initialize session state for cart and customer ID
if 'cart' not in st.session_state:
    st.session_state['cart'] = []
if 'customer_id' not in st.session_state:
    st.session_state['customer_id'] = None

def add_to_cart(product_id):
    st.session_state['cart'].append(product_id)
    cursor = st.session_state.db.cursor()
    cursor.execute("""
        INSERT INTO CustomerInteractions (customer_id, product_id, interaction_type)
        VALUES (%s, %s, 'cart_add')
    """, (st.session_state['customer_id'], product_id))
    st.session_state.db.commit()

def show_products():
    cursor = st.session_state.db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    for product in products:
        ## Fetch the image data as a BLOB
        #image_data = product['product_image']
        # Convert BLOB data to BytesIO object
        #image = BytesIO(image_data)
        #st.image(image, width=150, caption=product['product_name'])
        #image_data = product['product_image']
        st.write(product['product_description'])
        st.write(product['quantity'])
        st.write(f"Price: ${product['product_price']}")
        st.button('Add to Cart', key=f"add_to_cart_{product['product_id']}", on_click=add_to_cart, args=(product['product_id'],))
        st.write('---')

st.title("Products")
show_products()

