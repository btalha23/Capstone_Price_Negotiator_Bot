
import os
secret_key = os.urandom(24)
print(secret_key)

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import datetime

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = 'your_secret_key'


# MySQL Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="price_negotiation"
)

@app.route('/')
def index():
    return "Welcome to the B2B Ecommerce Website!"

@app.route('/products')
def products():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    return render_template('products.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("hello")
    if request.method == 'POST':
        
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        customer_email = request.form['customer_email']
        customer_location = request.form['customer_location']
        cursor = db.cursor()
        cursor.execute("INSERT INTO customer (first_name, last_name, customer_email,customer_location) VALUES (%s, %s, %s, %s)", 
                       (first_name, last_name, customer_email, customer_location))
        db.commit()
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        customer_email = request.form['customer_email']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer WHERE customer_email=%s", (customer_email,))
        customer = cursor.fetchone()
        if customer:
            session['customer_id'] = customer['customer_id']
            return redirect(url_for('products'))
    return render_template('login.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    customer_id = session.get('customer_id') # Assume the user is logged in and user_id is stored in the session
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True  # Mark the session as modified
    
    # Record the interaction in the database
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO CustomerInteractions (customer_id, product_id, interaction_type)
        VALUES (%s, %s, 'cart_add')
    """, (customer_id, product_id))
    db.commit()
    return redirect(url_for('products'))

@app.route('/checkout')
def checkout():
    if 'cart' not in session or not session['cart']:
        return "Your cart is empty"
    
    cursor = db.cursor(dictionary=True)
    cart_items = session['cart']
    placeholders = ', '.join(['%s'] * len(cart_items))
    query = f"SELECT * FROM Product WHERE product_id IN ({placeholders})"
    cursor.execute(query, cart_items)
    products = cursor.fetchall()
    return render_template('checkout.html', products=products)

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('checkout'))
    
    # Simulate order confirmation logic
    customer_id = session.get('customer_id')  # Assume the user is logged in and user_id is stored in the session
    
    if not customer_id:
        return "Error: Customer is not logged in", 400
    
    cart_items = session['cart']
    
    # Record the interaction in the database
    cursor = db.cursor()
    for product_id in cart_items:
        cursor.execute("""
            INSERT INTO CustomerInteractions (customer_id, product_id, interaction_type)
            VALUES (%s, %s, 'purchase')
        """, (customer_id, product_id))
    db.commit()
    
    # Here you would typically save the order details to your database
    
    # Clear the cart after order confirmation
    session.pop('cart', None)
    
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)