import streamlit as st
import mysql.connector
from PIL import Image   # We use pillow to handle image handling since Streamlit does not support local image handling by default.
import os
from io import BytesIO


# MySQL Configuration
db_conn = None
if 'db_mysql' not in st.session_state:
    db_conn = mysql.connector.connect(
        host="localhost",
        user="ahsan",
        password="MyNewPass1!",
        database="price_negotiation"
    )
    st.session_state.db_mysql = db_conn

# Initialize session state for cart and customer ID
if 'cart' not in st.session_state:
    st.session_state['cart'] = []
if 'customer_id' not in st.session_state:
    st.session_state['customer_id'] = None
    
    

def add_to_cart(product_id, quantity):
    st.session_state['cart'].append({'product_id': product_id, 'quantity': quantity})
    cursor = st.session_state.db_mysql.cursor()
    cursor.execute("""
        INSERT INTO CustomerInteractions (customer_id, product_id, interaction_type, quantity)
        VALUES (%s, %s, 'cart_add', %s)
    """, (st.session_state['customer_id'], product_id, quantity))
    st.session_state.db_mysql.commit()


def show_products():
    cursor = st.session_state.db_mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    for product in products:
        #st.image(f"./static/images/{product['product_image']}", width=150)
        # Display product image
        image_path = product.get('product_image', '').lstrip('/')
        if os.path.exists(image_path):
            image = Image.open(image_path)

            # Resize the image to half its size (Divide by a higher number to make it even smaller)
            new_size = (image.width // 2, image.height // 2)
            resized_image = image.resize(new_size)
            st.image(resized_image, caption=product.get("product_name", "Unnamed Product"), use_column_width=True)
        else:
            # If an image path does not lead to an image display this message
            st.write("Image not found")
        st.write(product['product_name'])
        st.write(product['product_description'])
        st.write(f"Price: ${product['product_price']}")
        quantity = st.number_input(f"Quantity for {product['product_id']}", min_value=10, max_value=1000, value=10, step=1, key=f"quantity_{product['product_id']}")
        #st.button('Add to Cart', key=f"add_to_cart_{product['product_id']}", on_click=add_to_cart, args=(product['product_id'], quantity))
        st.button('Add to Cart', key=f"add_to_cart_{product['product_id']}", on_click=add_to_cart, args=(product['product_id'], quantity))
        st.write('---')

st.title("Products")

if st.session_state['customer_id']:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
else:
    st.sidebar.write("Not logged in")
    
show_products()

