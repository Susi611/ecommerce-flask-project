from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "SECRET_KEY"

# =========================
# MongoDB Atlas Connection
# =========================
mongodb_uri = os.environ.get("mongodb_uri")

client = MongoClient(mongodb_uri)

try:
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print("❌ MongoDB Connection Error:", e)


db = client["EcommerceDB"]

users = db["users"]
admins = db["admins"]
products = db["products"]
orders = db["orders"]

if admins.count_documents({}) == 0:
    admins.insert_one({
        "username": "admin",
        "password": "admin123"
    })


# =========================
# HOME
# =========================
@app.route('/')
def home():
    return render_template("index.html")


# =========================
# USER REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        user = {
            "name": request.form['name'],
            "email": request.form['email'],
            "password": request.form['password']
        }

        users.insert_one(user)

        return redirect('/login')

    return render_template("register.html")


# =========================
# USER LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = users.find_one({
            "email": email,
            "password": password
        })

        if user:
            session['user'] = email
            return redirect('/products')

        return "Invalid User Login"

    return render_template("login.html")


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================
# PRODUCTS PAGE
# =========================
@app.route('/products')
def product_list():

    if 'user' not in session:
        return redirect('/login')

    all_products = list(products.find())

    return render_template("products.html", products=all_products)


# =========================
# SEARCH PRODUCTS
# =========================
@app.route('/search')
def search():

    keyword = request.args.get('keyword', '')

    results = list(products.find({
        "$or": [
            {
                "name": {
                    "$regex": keyword,
                    "$options": "i"
                }
            },
            {
                "brand": {
                    "$regex": keyword,
                    "$options": "i"
                }
            }
        ]
    }))

    return render_template(
        "products.html",
        products=results
    )
# =========================
# ADD TO CART
# =========================
@app.route('/add_cart/<id>')
def add_cart(id):

    if 'user' not in session:
        return redirect('/login')

    product = products.find_one({"_id": ObjectId(id)})

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(str(product['_id']))
    session.modified = True

    return redirect('/cart')


# =========================
# CART PAGE
# =========================
@app.route('/cart')
def cart():

    if 'user' not in session:
        return redirect('/login')

    cart_items = []

    for pid in session.get('cart', []):
        item = products.find_one({"_id": ObjectId(pid)})
        if item:
            cart_items.append(item)

    return render_template("cart.html", items=cart_items)


# =========================
# REMOVE FROM CART
# =========================
@app.route('/remove_cart/<id>')
def remove_cart(id):

    if 'cart' in session:
        session['cart'].remove(id)
        session.modified = True

    return redirect('/cart')


# =========================
# PLACE ORDER
# =========================
@app.route('/place_order')
def place_order():

    if 'user' not in session:
        return redirect('/login')

    order = {
        "customer": session['user'],
        "products": session.get('cart', []),
        "status": "Pending"
    }

    orders.insert_one(order)

    session['cart'] = []

    return redirect('/orders')


# =========================
# USER ORDERS
# =========================
@app.route('/orders')
def view_orders():

    if 'user' not in session:
        return redirect('/login')

    user_orders = list(orders.find({"customer": session['user']}))

    for order in user_orders:
        order_products = []

        for pid in order['products']:
            product = products.find_one({"_id": ObjectId(pid)})

            if product:
                order_products.append(product)

        order['product_details'] = order_products

    return render_template(
        "orders.html",
        orders=user_orders
    )

# =========================
# ADMIN LOGIN (MongoDB)
# =========================
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        admin = admins.find_one({
            "username": username,
            "password": password
        })

        if admin:
            session['admin'] = username
            return redirect('/admin/dashboard')

        return "Invalid Admin Login"

    return render_template("admin/login.html")


# =========================
# ADMIN DASHBOARD
# =========================
@app.route('/admin/dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    total_products = products.count_documents({})
    total_users = users.count_documents({})
    total_orders = orders.count_documents({})

    return render_template(
        "admin/dashboard.html",
        products=total_products,
        users=total_users,
        orders=total_orders
    )


# =========================
# ADD PRODUCT
# =========================
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():

    if 'admin' not in session:
        return redirect('/admin')

    if request.method == 'POST':

        product = {
            "name": request.form['name'],
            "price": request.form['price'],
            "image": request.form['image']
        }

        products.insert_one(product)

        return redirect('/admin/dashboard')

    return render_template("admin/add_product.html")


# =========================
# EDIT PRODUCT
# =========================
@app.route('/admin/edit/<id>', methods=['GET', 'POST'])
def edit_product(id):

    if 'admin' not in session:
        return redirect('/admin')

    product = products.find_one({"_id": ObjectId(id)})

    if request.method == 'POST':

        products.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": request.form['name'],
                "price": request.form['price'],
                "image": request.form['image']
            }}
        )

        return redirect('/admin/dashboard')

    return render_template("admin/edit_product.html", product=product)


# =========================
# DELETE PRODUCT
# =========================
@app.route('/admin/delete/<id>')
def delete_product(id):

    if 'admin' not in session:
        return redirect('/admin')

    products.delete_one({"_id": ObjectId(id)})

    return redirect('/admin/dashboard')


# =========================
# ADMIN ORDERS
# =========================
@app.route('/admin/orders')
def admin_orders():

    if 'admin' not in session:
        return redirect('/admin')

    all_orders = orders.find()

    return render_template("admin/manage_orders.html", orders=all_orders)


# =========================
# ACCEPT ORDER
# =========================
@app.route('/admin/accept/<id>')
def accept_order(id):

    orders.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "Accepted"}}
    )

    return redirect('/admin/orders')


# =========================
# REJECT ORDER
# =========================
@app.route('/admin/reject/<id>')
def reject_order(id):

    orders.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "Rejected"}}
    )

    return redirect('/admin/orders')


@app.route('/admin/customers')
def customers():

    if 'admin' not in session:
        return redirect('/admin')

    return render_template(
        'admin/customers.html',
        users=list(users.find())
    )


@app.route('/admin/analytics')
def analytics():

    if 'admin' not in session:
        return redirect('/admin')

    return render_template(
        'admin/analytics.html'
    )


@app.route('/admin/profile')
def profile():

    if 'admin' not in session:
        return redirect('/admin')

    return render_template(
        'admin/profile.html',
        products=products.count_documents({}),
        users=users.count_documents({}),
        orders=orders.count_documents({})
    )
# =========================
# RUN APP
# =========================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)