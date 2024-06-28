
import os
secret_key = os.urandom(24)
print(secret_key)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import datetime

from Chatbot_Text_Based_Interaction.src import nlp_processor
from Chatbot_Text_Based_Interaction.src.resources import dataset as ds

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

# Initialize the ChatBot
nlp = nlp_processor.NLP_Block(ds.pre_defined_responses)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    return render_template('products.html', products=products)

# Handling adding to Cart locally
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product WHERE product_id=%s", (product_id,))
    product = cursor.fetchone()
    
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(product)
    session.modified = True

    return redirect(url_for('products'))

# Handling removing from Cart locally
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
        session.modified = True

    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' in session:
        user_email = session['user']['user_email']
    else:
        user_email = None

    # Initialize cart and chat log in session if not already present
    if 'cart' not in session:
        session['cart'] = []

    if 'chat_log' not in session:
        session['chat_log'] = []

    if request.method == 'POST':
        if request.form['action'] == 'add_to_cart':
            product_id = int(request.form['product_id'])
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Product WHERE product_id=%s", (product_id,))
            product = cursor.fetchone()
            if product:
                session['cart'].append(product)
                session.modified = True
        
        elif request.form['action'] == 'remove_from_cart':
            product_id = int(request.form['product_id'])
            session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
            session.modified = True

        elif request.form['action'] == 'purchase':
            # Handle purchase logic here if needed
            pass
        
        elif request.form['action'] == 'negotiate':
            user_input = request.form['negotiate_input']
            response = nlp.get_response(user_input)
            session['chat_log'].append({'user': user_input, 'bot': response})

    cart = session['cart']
    total_price = calculate_total_price(cart)  # Calculate total price based on cart items

    return render_template('checkout.html', user_email=user_email, cart=cart, total_price=total_price, chat_log=session['chat_log'])


# Function to calculate total price of items in the cart
def calculate_total_price(cart):
    total_price = 0
    for item in cart:
        total_price += item['product_price']
    return total_price


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_email = request.form['user_email']
        user_location = request.form['user_location']
        cursor = db.cursor()
        cursor.execute("INSERT INTO User (first_name, last_name, user_email, user_location) VALUES (%s, %s, %s, %s)", 
                       (first_name, last_name, user_email, user_location))
        db.commit()
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['user_email']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM User WHERE user_email=%s", (user_email,))
        user = cursor.fetchone()
        if user:
            session['user'] = user
            return redirect(url_for('products'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('cart', None)
    session.pop('chat_log', None)
    return redirect(url_for('index'))

@app.route('/negotiate', methods=['POST'])
def negotiate():
    data = request.json
    product_id = data.get('product_id')
    units = data.get('units')

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT product_price FROM Product WHERE product_id=%s", (product_id,))
    product = cursor.fetchone()
    original_price = product['product_price'] * units

    user_input = f"Negotiate price for {units} units of product {product_id}"
    response = nlp.get_response(user_input)
    negotiated_price = original_price * 0.9  # Example of a simple negotiation logic

    return jsonify({
        'original_price': original_price,
        'negotiated_price': negotiated_price,
        'response': response
    })

if __name__ == '__main__':
    app.run(debug=True)