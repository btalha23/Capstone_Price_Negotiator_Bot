import streamlit as st
import mysql.connector

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
if 'redirect_to_login' not in st.session_state:
    st.session_state['redirect_to_login'] = False

def add_to_cart(product_id, quantity):
    st.session_state['cart'].append({'product_id': product_id, 'quantity': quantity})
    cursor = st.session_state.db.cursor()
    cursor.execute("""
        INSERT INTO CustomerInteractions (customer_id, product_id, interaction_type, quantity)
        VALUES (%s, %s, 'cart_add', %s)
    """, (st.session_state['customer_id'], product_id, quantity))
    st.session_state.db.commit()

def show_products():
    cursor = st.session_state.db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    for product in products:
        #st.image(f"./static/images/{product['product_image']}", width=150)
        st.write(product['product_name'])
        st.write(product['product_description'])
        st.write(f"Price: ${product['product_price']}")
        quantity = st.number_input(f"Quantity for {product['product_id']}", min_value=10, max_value=1000, value=10, step=1, key=f"quantity_{product['product_id']}")
        #st.button('Add to Cart', key=f"add_to_cart_{product['product_id']}", on_click=add_to_cart, args=(product['product_id'], quantity))
        st.button('Add to Cart', key=f"add_to_cart_{product['product_id']}", on_click=add_to_cart, args=(product['product_id'], quantity))
        st.write('---')
        
    if st.button('Go to Checkout'):
        st.experimental_set_query_params(page="Checkout")
        st.experimental_rerun()

def checkout():
    if not st.session_state['cart']:
        st.write("Your cart is empty")
        return
    
    cursor = st.session_state.db.cursor(dictionary=True)
    cart_items = [item['product_id'] for item in st.session_state['cart']]
    placeholders = ', '.join(['%s'] * len(cart_items))
    query = f"SELECT * FROM Product WHERE product_id IN ({placeholders})"
    cursor.execute(query, cart_items)
    products = cursor.fetchall()

    st.write("### Checkout")
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
        confirm_order()
    
    
def confirm_order():
    if not st.session_state['cart']:
        st.experimental_set_query_params(page="Checkout")
        st.experimental_rerun()
        return

    customer_id = st.session_state.get('customer_id')
    if not customer_id:
        st.write("Error: Customer is not logged in")
        return

    cart_items = st.session_state['cart']
    cursor = st.session_state.db.cursor()
    for item in cart_items:
        cursor.execute("""
            INSERT INTO CustomerInteractions (customer_id, product_id, interaction_type, quantity)
            VALUES (%s, %s, 'purchase', %s)
        """, (customer_id, item['product_id'], item['quantity']))
    st.session_state.db.commit()

    # Clear the cart after order confirmation
    st.session_state['cart'] = []
    st.write("Order confirmed! Thank you for your purchase.")
    
        
def register():
    st.title("Register")
    st.write("New Customers - Please Register Customer Info Here")

    user_input_first_name = st.text_input("First Name")
    user_input_last_name = st.text_input("Last Name")
    user_input_customer_email = st.text_input("Customer Email")
    user_input_customer_location = st.text_input("Customer Location")

    if st.button("Register"):
        with st.spinner("Connecting to database..."):
            cursor = st.session_state.db.cursor()
            sql_command = """
                INSERT INTO Customer (first_name, last_name, customer_email, customer_location)
                VALUES (%s, %s, %s, %s)
            """
            sql_parameters = (user_input_first_name, user_input_last_name, user_input_customer_email, user_input_customer_location)
            cursor.execute(sql_command, sql_parameters)
            st.session_state.db.commit()
            st.success("User Registered Successfully")
            st.session_state['redirect_to_login'] = True
            st.experimental_rerun()

def login():
    st.title("Login")
    customer_email = st.text_input('Email')
    if st.button('Login'):
        cursor = st.session_state.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer WHERE customer_email=%s", (customer_email,))
        customer = cursor.fetchone()
        if customer:
            st.session_state['customer_id'] = customer['customer_id']
            st.success("Logged in successfully")
            st.experimental_rerun()

def main():
    if st.session_state['redirect_to_login']:
        st.session_state['redirect_to_login'] = False
        st.experimental_set_query_params(page="Login")
        st.experimental_rerun()

    st.title("B2B Ecommerce Website")
    if st.session_state['customer_id']:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
    else:
        st.sidebar.write("Not logged in")

    page = st.sidebar.selectbox("Choose a page", ["Products", "Checkout", "Login", "Register"])

    if page == "Products":
        show_products()
    elif page == "Checkout":
        checkout()
    elif page == "Login":
        login()
    elif page == "Register":
        register()

if __name__ == '__main__':
    main()
