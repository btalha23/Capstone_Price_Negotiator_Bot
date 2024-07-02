import streamlit as st
import mysql.connector
from PIL import Image   # We use pillow to handle image handling since Streamlit does not support local image handling by default.
import os # We use OS for declaring our image pathing form the DB and checking if it exists locally.

# Note - Run pip install pillow <--

# Set up MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="price_negotiation"
)

# Page Title
st.title("Products")

# Fetch products from the DB
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT * FROM Product")
products = cursor.fetchall()

# Display our products from the DB
if products:
    for product in products:
        st.subheader(product.get("product_name", "Unnamed Product"))
        
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
        
        # If a product is missing a field these will be the default values
        st.write(f"Price: {product.get('product_price', 'N/A')}")
        st.write(f"Description: {product.get('product_description', 'No description available')}")
        
        if st.button(f"Add to cart", key=product["product_id"]):
            # Add product to cart
            if 'cart' not in st.session_state:
                st.session_state['cart'] = []
            st.session_state['cart'].append(product)
            st.success(f"{product.get('product_name', 'Unnamed Product')} added to cart!")
else:
    # If no products are found or the DB is innaccesible this is the default case
    st.write("No products available.")
