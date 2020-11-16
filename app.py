from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta 
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import yaml
#from flask_sqlalchemy import sqlalchemy


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
            cursor.execute('SELECT last_name FROM buyers WHERE email = %s AND password = %s',(user,password))
            last_name = cursor.fetchone()
            cursor.execute('SELECT currentBalance FROM buyers WHERE email = %s AND password = %s',(user,password))
            balance = cursor.fetchone()
            cursor.execute('SELECT userID FROM buyers WHERE email = %s AND password = %s',(user,password))
            userID = cursor.fetchone()
            #Give email (user), password, first_name, userID variables to the session 
            print(balance)
            print(last_name)
            session["first_name"] = first_name[0]
            session["last_name"] = last_name[0]
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
    return "<h1>Sorry dude; tough luck</h1>"

# Logout page, clears session
@app.route("/logout")
def logout():
    # notifies that you've been logged out
    flash("You have been logged out", "info") #warning, info, error
    # Pops the user info out of the session
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("home"))

# UNFINISHED; GET & DISPLAY ALL USER DATA
@app.route("/user", methods = ["POST", "GET"])
def user():
   if "user" in session:
       logvar = True
       first_name = session["first_name"]
       userID = session["userID"]
       seller = session["seller"]
       # Open cursor to get all details about user
       cursor = mysql.connection.cursor()
       cursor.execute('SELECT * FROM buyers WHERE userID = %s', [userID])
       # All user data stored in Buyers: (userID, email, password,
       #   currentBalance, first_name, last_name, image)
       info = cursor.fetchone()
       return render_template("user.html", logvar = logvar, first_name = first_name, seller = seller, info = info)
   else:
       flash("You are not logged in!")
       return redirect(url_for("login"))


# UNFINISHED; REGISTER NEW USER
@app.route("/registration", methods = ["POST", "GET"])
def registration():
   if "user" in session:
       flash("You are already logged in! Logout to register as different user.")
       return redirect(url_for("user"))
   elif request.method == "POST":
       # INSERT FUNCTIONAL CODE HERE
       # Once you register as a user, you have to log in as
       # the new user to access site, so redirect to login
       cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
 
       password = request.form["password"]
       confirmation = request.form["confirmedpw"]
       if(password != confirmation):
           flash("Whoops! Your password and confirmed password don't match!")
           return redirect(url_for("registration"))
 
       email = request.form["email"]
       cursor.execute('SELECT email FROM buyers WHERE email = %s',[email])
       if_email_exists = cursor.fetchone()
       if(if_email_exists == email):
           flash("Whoops! A user with this email already exists. Please login with this address or register with a different one.")
           return redirect(url_for("registration"))
 
       first = request.form["first_name"]
       last = request.form["last_name"]
       org_name = request.form["org_name"]
       descr = request.form["description"]
       ifSeller = request.form.get("sellercheck")
 
       # Determine New Unique UserID
       cursor.execute('SELECT max(userID) as A FROM Buyers')
       maxID = cursor.fetchone()
       if(maxID == None): maxID = 0
       print(maxID)
       userID = maxID["A"] + 1
 
       # Create User in Buyers
       # Buyers(userID, email, password, currentBalance, firstname, lastname, image)
           # TODO: FIGURE OUT IMAGE SITUATION
       cursor.execute('INSERT INTO Buyers VALUES(%s, %s, %s, %s, %s, %s, %s)',[userID, email, password, 0.00, first, last, None])
       mysql.connection.commit()
 
       # INSERT INTO table(column1, column2,...) VALUES (value1, value2,...);
 
       # Create a seller with the same UserID if seller is checked
       # Sellers(userID, organization, image, description, avg_rating)
       if(ifSeller == "true"):
           cursor.execute('INSERT INTO Sellers VALUES(%s, %s, %s, %s, %s)',[userID, org_name, None, descr, 0.00])
           mysql.connection.commit()
 
       # If exists in database -> email already in use
       flash("Thank you for registering as a new user!")
       return redirect(url_for("login"))
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
            cursor.execute('DELETE FROM items WHERE itemID = %s',(item_id,))
            mysql.connection.commit() # This commits the change to the actual mysql database
            return redirect(url_for("seller"))
        return render_template("seller.html", logvar = logvar, first_name = first_name, seller = seller, items = items)
    else: # If you somehow accessed this page and weren't logged in
        flash("You are not logged in as a seller")
        return redirect(url_for("home"))

@app.route("/addbalance")
def addbalance():
   if "user" in session: # Check if user is logged in
       logvar = True # Update logvar boolean if so
       # Retrieve session data
       first_name = session["first_name"]
       userID = session["userID"]
       # Open a cursor and get current balance for user
       cursor = mysql.connection.cursor()
       cursor.execute('SELECT currentBalance FROM buyers WHERE userID = %s', [userID])
       currentBalance = cursor.fetchone()
       return render_template("addbalance.html", logvar = logvar, first_name = first_name, currentBalance = currentBalance)
   else: # If you somehow accessed this page and weren't logged in
       flash("You are not logged in to add balance")
       return redirect(url_for("home"))

@app.route("/purchasehistory")
def purchasehistory():
    return render_template("purchasehistory.html")

# GET EMPLOYEE
@app.route('/update/<id>', methods =["POST","GET"])
def update(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM items WHERE itemID = %s',[id])
    item = cursor.fetchall()
    cursor.close()
    print(item)
    return render_template("modify.html", item = item)

# UPDATE EMPLOYEE
@app.route('/modify/<id>', methods = ["POST","GET"])
def moditem(id):
    if "user" in session and session["seller"] == True:
        if request.method == 'POST':
            logvar = True
            sellerID = session["userID"]
            first_name = session["first_name"]
            # Get variables from previous form
            newname = request.form['newname']
            newprice = request.form['newprice']
            newcount = request.form['newcount']
            newdesc = request.form['newdesc']
            #newimage= request.form['newimage']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE items SET name = %s, price = %s, num = %s, description = %s WHERE itemID = %s',[newname, newprice, newcount, newdesc, id])
            flash('Item Updated Successfully')
            mysql.connection.commit()
            return redirect(url_for("seller"))
    else: # If you somehow accessed this page and weren't logged in
        flash("You are not logged in/a seller")
        return redirect(url_for("home"))

@app.route('/additemspage')
def additemspage():
    if "user" in session and session["seller"] == True:
        logvar = True
        first_name = session["first_name"]
        return render_template("additems.html", logvar = logvar, first_name = first_name)
    else:
        flash("You are not logged in/a seller")
        return redirect(url_for("home"))




@app.route('/additems', methods = ['POST','GET'])
def additems():
    if "user" in session and session["seller"] == True:
        logvar = True
        first_name = session["first_name"]
        if request.method == "POST":
            sellerID = session["userID"]
            itemname = request.form['name']
            price = request.form['price']
            count = request.form['num']
            description = request.form['desc']
            image = request.form['image']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT max(itemID) as A FROM items')
            maxID = cursor.fetchone()
            if(maxID == None): maxID = 0
            print(maxID)
            itemID = maxID["A"] + 1
            avg_rating = 0.00
            cursor.execute('INSERT INTO items VALUES(%s, %s, %s, %s, %s, %s, %s, NULL)',[itemID, sellerID, itemname, price, avg_rating, count, description])
            mysql.connection.commit()
            flash("Item successfully added")
            return redirect(url_for("additemspage"))
    else:
        flash("You are not logged in/a seller")
        return redirect(url_for("home"))
    




if __name__ == "__main__":
    app.run(debug=True)