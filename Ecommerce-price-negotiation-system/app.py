import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime

app = Flask(__name__)

app.secret_key = os.urandom(24)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

# Flask SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define models
class Product(db.Model):
    __tablename__ = 'Product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.Float, nullable=False)

class Customer(db.Model):
    __tablename__ = 'Customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False, unique=True)
    customer_location = db.Column(db.String(255), nullable=False)

class CustomerInteraction(db.Model):
    __tablename__ = 'CustomerInteractions'
    interaction_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.customer_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.product_id'), nullable=False)
    interaction_type = db.Column(db.String(255), nullable=False)

@app.route('/')
def index():
    return "Welcome to the B2B Ecommerce Website!"

@app.route('/products')
def products():
    try:
        products = Product.query.all()
        return render_template('products.html', products=products)
    except SQLAlchemyError as e:
        return str(e)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        customer_email = request.form['customer_email']
        customer_location = request.form['customer_location']
        new_customer = Customer(
            first_name=first_name,
            last_name=last_name,
            customer_email=customer_email,
            customer_location=customer_location
        )
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        customer_email = request.form['customer_email']
        customer = Customer.query.filter_by(customer_email=customer_email).first()
        if customer:
            session['customer_id'] = customer.customer_id
            return redirect(url_for('products'))
    return render_template('login.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    customer_id = session.get('customer_id')  # Assume the user is logged in and user_id is stored in the session
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True  # Mark the session as modified

    # Record the interaction in the database
    new_interaction = CustomerInteraction(
        customer_id=customer_id,
        product_id=product_id,
        interaction_type='cart_add'
    )
    db.session.add(new_interaction)
    db.session.commit()
    return redirect(url_for('products'))

@app.route('/checkout')
def checkout():
    if 'cart' not in session or not session['cart']:
        return "Your cart is empty"
    
    cart_items = session['cart']
    products = Product.query.filter(Product.product_id.in_(cart_items)).all()
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
    for product_id in cart_items:
        new_interaction = CustomerInteraction(
            customer_id=customer_id,
            product_id=product_id,
            interaction_type='purchase'
        )
        db.session.add(new_interaction)
    db.session.commit()

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
