from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta 
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import yaml
from flask_sqlalchemy import sqlalchemy


# Substantiate flaskapp
app = Flask(__name__)

# Make secret key for session data
app.secret_key = "yeet"

# Configure dbs
# CHECK DB.YAML FILE TO SEE IF ALL OF THE PARAMETERS MATCH ON YOUR LOCAL MACHINE
# FOR LOCAL MACHINE: USER: 'ROOT' PASSWORD: 'password'
# This is just for Rj's local machine^^ you probably have your own password
# CURRENTLY THE VM PASSWORD IS WHAT'S UPLAODED
# FOR VM USER: 'user' PASSWORD: 'HEJDIhsdf83-Q'
#
db = yaml.load(open('./templates/db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password'] #THIS WILL BE DIFFERENT, CHECK YAML FILE AND CHANGE ACCORDINGLY, ALSO DON'T PUSH THE YAML
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)

# Home page, renders homepage.html
@app.route("/")
def home():
    if "user" in session:
        logvar = True 
        first_name = session["first_name"]
        return render_template("homepage.html", logvar = logvar, first_name = first_name)
    else:
        logvar = False
    return render_template("homepage.html", logvar = logvar)





# Login page, renders login.html and gets session values for
# firstname
# user (email)
# password
# seller (boolean)
@app.route("/login", methods = ["POST","GET"])
def login():
    if request.method == "POST": # If the method that is called in login.html is a post method
        # Store Values from the form into user and password variables
        user = request.form["nm"]
        password = request.form["pw"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # This opens a cursor that can interact with the databases
        cursor.execute('SELECT * FROM buyers WHERE email = %s AND password = %s',(user,password)) # Selects all buyers where email and password both match
        account = cursor.fetchone() # takes one of these instances into account
        if account: # If succesfully found in database
            cursor =  mysql.connection.cursor() #Opens another Cursor
            cursor.execute('SELECT first_name FROM buyers WHERE email = %s AND password = %s',(user,password))
            first_name = cursor.fetchone()
            cursor.execute('SELECT userID FROM buyers WHERE email = %s AND password = %s',(user,password))
            userID = cursor.fetchone()
            #Give email (user), password, first_name, userID variables to the session 
            session["first_name"] = first_name[0]
            session["userID"] = userID[0]
            session["user"] = user
            session["password"] = password
            # Check seller table to see if buyer/user is also a seller
            userID = session["userID"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM sellers WHERE userID = %s', [userID])
            seller = cursor.fetchone()
            # Set session seller status to corresponding boolean 
            if seller:
                session["seller"] = True
            else:
                session["seller"] = False
            flash("Login Succesful!") # Flash a message that says login succesful 
            return redirect(url_for("home")) # Redirects to home page
        else: # If login is unsuccesful
            # Redirects to login page and flashes a message that login was incorrect
            flash("Incorrect Login!") 
            return redirect(url_for("login"))
    # If no method call 
    else:
        # if already logged in 
        if "user" in session:
            flash("Already Logged in!")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/forgotpw")
def forgotpw():
    return "<h1>Sorry dude tough luck</h1>"

# Logout page, clears session
@app.route("/logout")
def logout():
    # notifies that you've been logged out
    flash("You have been logged out", "info") #warning, info, error
    # Pops the user info out of the session
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("home"))


@app.route("/user", methods = ["POST", "GET"])
def user():
    if "user" in session:
        logvar = True
        first_name = session["first_name"]
        seller = session["seller"] 
        return render_template("user.html", logvar = logvar, first_name = first_name, seller = seller)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/searchresults")
def searchresults():
    return render_template("search_results.html")

@app.route("/item")
def item():
    return render_template("item.html")

@app.route("/addreview")
def addreview():
    return render_template("addreview.html")

@app.route("/seller", methods = ["POST","GET"])
def seller():
    if "user" in session and session["seller"] == True: # Check if user is logged in
        logvar = True # Update logvar boolean if so
        # Retrieve session data
        first_name = session["first_name"] 
        sellerID = session["userID"]
        seller = session["seller"]
        # Open a cursor and get all items sold for a seller
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT itemID, name, price, num, image FROM items WHERE sellerID = %s', [sellerID])
        items = cursor.fetchall()
        # This is where the delete function is implemented
        if request.method == "POST":
            item_id = request.form["item_id"]
            session["clicked_item"] = item_id
            cursor.execute('DELETE FROM items WHERE itemID = %s',(item_id,))
            mysql.connection.commit() # This commits the change to the actual mysql database
            return redirect(url_for("seller"))
        return render_template("seller.html", logvar = logvar, first_name = first_name, seller = seller, items = items)
    else: # If you somehow accessed this page and weren't logged in
        flash("You are not logged in/a seller")
        return redirect(url_for("home"))

@app.route("/addbalance")
def addbalance():
    return render_template("addbalance.html")

@app.route("/purchasehistory")
def purchasehistory():
    return render_template("purchasehistory.html")

@app.route('/moditems', methods = ["POST","GET"])
def moditems():
    logvar = True
    first_name = session["first_name"]
    sellerID = session["userID"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT itemID, name, price, num, image FROM items WHERE sellerID = %s', [sellerID])
    items = cursor.fetchall()
    if request.method == "POST":
            item_id = request.form["item_id"]
            session["clicked_item"] = item_id
            
    return render_template("modify.html", logvar = logvar, first_name = first_name, items=items )

@app.route('/delitems')
def delitems():
    return render_template("delitems.html")


@app.route('/additems')
def additems():
    return render_template("additems.html")


# @app.route("/account/seller", methods =['GET', 'POST'])
# def seller():
#     if request.method == 'POST':
#         #Fetch form data
#         marketDetails = request.form
#         item = marketDetails['item']
#         price = marketDetails['price']
#         quantity = marketDetails['quantity']
#         seller = marketDetails['seller']
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO market(item, price, quantity, seller) VALUES(%s, %s, %s, %s)", (item, price, quantity, seller))
#         mysql.connection.commit()
#         cur.close()
#         #return redirect('/display')
#     return render_template("seller_items.html")


# @app.route('/display')
# def display():
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute("SELECT * FROM market")
#     if resultValue > 0:
#         marketDetails = cur.fetchall()
#         return render_template('market.html',marketDetails = marketDetails)

if __name__ == "__main__":
    app.run(debug=True)