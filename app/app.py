from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

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
            print("hello user")
            return redirect(url_for('products'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)