from flask import Flask, request, render_template, redirect, url_for, session,jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os  # Add this import for directory handling

app = Flask(__name__)
from datetime import timedelta

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session expires after 30 minutes

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'database1'
app.secret_key = 'your_secret_key'  # You should set a secret key for session management

mysql = MySQL(app)

# Create the users table if not exists (Inside app context)
with app.app_context():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );
    ''')
    mysql.connection.commit()

def upload_product_image(image_path):
    # Configuration
    cloudinary.config(
        cloud_name="dzucf3efo",
        api_key="737822546693835",
        api_secret="tGe-c9sbZcaXJmo5BMHoaKmI4F4",  # Replace with actual API secret
        secure=True
    )
    
    # Upload image to Cloudinary under 'products' folder
    upload_result = cloudinary.uploader.upload(
        image_path,
        folder="products"  # Saves image inside 'products' folder
    )
    
    # Get the secure URL of the uploaded image
    image_url = upload_result.get("secure_url")
    print(f"Uploaded Image URL: {image_url}")
    
    return image_url
# Route for login details
@app.route('/login_details', methods=['POST'])
def login_details():
    email = request.form['email']
    password = request.form['password']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if(email=="admin@gmail.com" and password=="adminpassword"):
        return redirect(url_for('adminlanding'))
    # Query the users table
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        # If password is correct, redirect to success page
        session['user_id'] = user['id']  # Store user id in session
        session.permanent = True  # This ensures the session follows PERMANENT_SESSION_LIFETIME
        print(user['role'])
        if (user['role']=='user'):
            return redirect(url_for('mininew'))
        elif (user['role']=='seller'):
            return redirect(url_for('sellerlanding'))
        
            
    else:
        # If login fails, redirect to failure page
        return redirect(url_for('login_failure'))


@app.route('/getfooditems', methods=['GET'])
def get_food_items():
    try:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch food items with category 'Homemade Food'
        cursor.execute("SELECT * FROM items WHERE category = %s", ('Homemade Food',))
        items = cursor.fetchall()

        
        return jsonify([dict(item) for item in items])

    except Exception as e:
        return jsonify({"error": str(e)}), 500  

@app.route('/getcraftitems', methods=['GET'])
def get_craft_items():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch items with category 'Crafts'
        cursor.execute("SELECT * FROM items WHERE category = %s", ('Crafts',))
        items = cursor.fetchall()

        return jsonify([dict(item) for item in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
     
@app.route('/getpaintings', methods=['GET'])
def get_paintings():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch painting items with category 'Paintings'
        cursor.execute("SELECT * FROM items WHERE category = %s", ('Paintings',))
        items = cursor.fetchall()

        # Return the items as JSON
        return jsonify([dict(item) for item in items])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getitems/<string:category>', methods=['GET'])
def get_items_by_category(category):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch items based on the category
        cursor.execute("SELECT * FROM items WHERE category = %s", (category,))
        items = cursor.fetchall()

        # Return the items as JSON
        return jsonify([dict(item) for item in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getcartitems', methods=['GET'])
def get_cart_items():
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return jsonify([])  # Return an empty list if the user is not logged in

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, title, price, image FROM cart WHERE user_id = %s", (user_id,))
        items = cursor.fetchall()

        return jsonify([dict(item) for item in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/removecartitem/<int:item_id>', methods=['DELETE'])
def remove_cart_item(item_id):
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM cart WHERE id = %s AND user_id = %s", (item_id, user_id))
        mysql.connection.commit()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Route for registration
@app.route('/registration', methods=['POST']) 
def registration():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    role = request.form['role']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#jacob
    # Check if the username already exists
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()

    if user:
        # If the user exists, redirect to failure page
        return redirect(url_for('registration_failure'))
    else:
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert the new user into the users table
        cursor.execute('INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s , %s)', 
                       (username, email, hashed_password, role))
        mysql.connection.commit()
        return redirect(url_for('slogin'))

@app.route('/addtocart', methods=['POST'])
def add_to_cart():
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401  # User must be logged in

        # Get item details from the request
        item_id = request.form.get('item_id')
        title = request.form.get('title')
        price = request.form.get('price')
        image = request.form.get('image')

        # Insert the item into the cart table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO cart (user_id, itemid, title, price, image) VALUES (%s, %s, %s, %s, %s)",
            (user_id, item_id, title, price, image)
        )
        mysql.connection.commit()

        return jsonify({"success": True, "message": "Item added to cart successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/addtowishlist', methods=['POST'])
def add_to_wishlist():
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401  # User must be logged in

        # Get item details from the request
        item_id = request.form.get('item_id')
        title = request.form.get('title')
        price = request.form.get('price')
        image = request.form.get('image')

        # Insert the item into the wishlist table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO wishlist (user_id, item_id, title, price, image) VALUES (%s, %s, %s, %s, %s)",
            (user_id, item_id, title, price, image)
        )
        mysql.connection.commit()

        return jsonify({"success": True, "message": "Item added to wishlist successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getwishlist', methods=['GET'])
def get_wishlist():
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return jsonify([])  # Return an empty list if the user is not logged in

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, item_id, title, price, image FROM wishlist WHERE user_id = %s", (user_id,))
        items = cursor.fetchall()

        return jsonify([dict(item) for item in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/removewishlistitem/<int:item_id>', methods=['DELETE'])
def remove_wishlist_item(item_id):
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM wishlist WHERE id = %s AND user_id = %s", (item_id, user_id))
        mysql.connection.commit()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for index page
@app.route('/')
def index():
    return render_template('landing.html')

# Other routes for various pages
# @app.route('/blogin')
# def blogin():
#     return render_template('blogin.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/crafts')
def crafts():
    return render_template('crafts.html')

@app.route('/food')
def food():
    return render_template('food.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

@app.route('/mininew')
def mininew():
    return render_template('mininew.html')

@app.route('/painting')
def painting():
    return render_template('painting.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/ptj')
def ptj():
    return render_template('ptj.html')

@app.route('/sellerlogin')
def sellerlogin():
    return render_template('sellerlogin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/sellerlanding')
def sellerlanding():
    return render_template('sellerlanding.html')

@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin')

@app.route('/admin')
def admin():
    return render_template('admin')

@app.route('/adminlanding')
def adminlanding():
    return render_template('adminlanding.html')

@app.route('/adminfood')
def adminfood():
    return render_template('adminfood.html')

ADMIN_PASSWORD_HASH = generate_password_hash("adminpassword")  # Replace "adminpassword" with your actual password

@app.route('/adminloging', methods=['GET', 'POST'])
def adminloging():
    if request.method == 'POST':
        password = request.form.get('password')

        # Validate the admin password
        if check_password_hash(ADMIN_PASSWORD_HASH, password):  # Compare the hashed password
            return redirect(url_for('adminlanding'))  # Redirect to admin landing page
        else:
            return render_template('adminlogin.html', error="Invalid password")  # Show error message

    return render_template('adminlogin.html')

@app.route('/adminpainting')
def adminpainting():
    return render_template('adminpainting.html')

# @app.route('/slogin')
# def slogin():
#     return render_template('slogin.html')

@app.route('/sellermyprofile', methods=['GET', 'POST'])
def sellermyprofile():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        bio = request.form.get('bio')
        image_file = request.files['image']
        userid= session.get('user_id') 
        image_url = upload_product_image(image_file)
        # Process the data (e.g., save to database)
        # For now, just print it to the console
        print(f"Name: {name}, Email: {email}, Phone: {phone}, Address: {address}, Bio: {bio}")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO sellerusers (name, email, phone, address, bio,image_url,userid) VALUES (%s, %s, %s, %s, %s , %s ,%s)', 
                       (name, email, phone, address, bio,image_url,userid))
        mysql.connection.commit()
        # Redirect to a success page or reload the profile page
        return redirect(url_for('sellerlanding'))

    return render_template('sellermyprofile.html')

@app.route('/uploaditems', methods=['POST'])
def uploaditems():
    try:
        # Get the logged-in user's ID
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401  # User must be logged in

        # Get form data
        title = request.form.get('title')
        price = request.form.get('price')
        desc = request.form.get('desc')
        category = request.form.get('category')
        image_file = request.files['image']
        print(title,price,desc,category,image_file)

        # Validate the data
        if not title or not price or not desc or not category or not image_file:
            return jsonify({"error": "All fields are required."}), 400

        # Upload the image to Cloudinary or save it locally
        image_url = upload_product_image(image_file)

        # Insert the item into the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO items (title, price, description, category, user_id, image) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, price, desc, category, user_id, image_url)
        )
        mysql.connection.commit()

        return jsonify({"success": True, "message": "Item added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/slogin', methods=['GET', 'POST'])
def slogin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user from database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sellerusers WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user and user['password'] == password:  # Ensure you store passwords securely (e.g., hashed)
            # session['loggedin'] = True
            # session['id'] = user['id']
            # session['name'] = user['name']
            return redirect(url_for('sellermyprofile'))  # Redirect to the profile page
        
    
    return render_template('slogin.html')  # Render login page

@app.route('/submitjoboffer', methods=['POST'])
def submit_job_offer():
    try:
        # Parse the JSON data from the request
        data = request.get_json()
        #name = data.get('name')  # Add the 'name' field
        title = data.get('title')
        description = data.get('description')
        contact = data.get('contact')
        uid=session.get('user_id')
        # Validate the data
        if   not title or not description or not contact:
            return jsonify({"success": False, "error": "All fields are required."}), 400

        # Insert the job offer into the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO job_offers (name, title, description, contact) VALUES (%s, %s, %s, %s)",
            (uid, title, description, contact)
        )
        mysql.connection.commit()

        return jsonify({"success": True, "message": "Job offer submitted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/getjoboffers', methods=['GET'])
def get_job_offers():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM job_offers")
        job_offers = cursor.fetchall()
        return jsonify(job_offers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_users_items', methods=['GET'])
def get_users_items():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
        SELECT 
            users.id AS user_id, 
            users.username, 
            users.email, 
            users.role,
            items.id AS item_id, 
            items.title AS item_title, 
            items.price, 
            items.description, 
            items.category, 
            items.image
        FROM users
        LEFT JOIN items ON users.id = items.user_id
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # Organizing the response
        users_dict = {}
        for row in data:
            user_id = row["user_id"]
            if user_id not in users_dict:
                users_dict[user_id] = {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "email": row["email"],
                    "role": row["role"],
                    "items": []
                }
            if row["item_id"]:  # If the user has an item
                users_dict[user_id]["items"].append({
                    "item_id": row["item_id"],
                    "title": row["item_title"],
                    "price": float(row["price"]),  # Convert Decimal to float
                    "description": row["description"],
                    "category": row["category"],
                    "image": row["image"]
                })

        return jsonify(list(users_dict.values()))  # Convert to JSON list
    except Exception as e:
        return jsonify({"error": str(e)}), 500

### **DELETE USER (AND THEIR ITEMS)**
@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        cursor = mysql.connection.cursor()

        # First, delete all items associated with the user
        cursor.execute("DELETE FROM items WHERE user_id = %s", (user_id,))

        # Then, delete the user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()

        return jsonify({"message": "User and their items deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

### **DELETE ITEM**
@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        cursor = mysql.connection.cursor()

        # Delete the item
        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        mysql.connection.commit()

        return jsonify({"message": "Item deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sellitem/<string:category>', methods=['POST'])
def sell_item(category):
    try:
        user_id = session.get('user_id')  # Ensure the user is logged in
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        title = request.form.get('title')
        price = request.form.get('price')
        desc = request.form.get('desc')
        image = request.files.get('image')

        if not (title and price and desc and image):
            return jsonify({"error": "All fields are required"}), 400

        # Ensure the uploads directory exists
        upload_dir = os.path.join('static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the image to the server
        image_path = os.path.join(upload_dir, image.filename)
        image.save(image_path)

        # Insert the item into the database
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO items (user_id, title, price, description, category, image) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, title, price, desc, category, image_path)
        )
        mysql.connection.commit()

        return jsonify({"success": True, "message": "Item posted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # Clear user session
    return redirect('/landing')  # Redirect to landing page
# Success or failure pages
@app.route('/login_success')
def login_success():
    return 'Login successful!'

@app.route('/login_failure')
def login_failure():
    return 'Login failed! Please check your username and password.'

@app.route('/registration_success')
def registration_success():
    return 'Registration successful!'

@app.route('/registration_failure')
def registration_failure():
    return 'Registration failed! Username already exists.'

if __name__ == '__main__':
    app.run(debug=True)


