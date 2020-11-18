from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_mail import Mail, Message # YOU HAVE TO INSTALL FLASK-MAIL: pip install flask-mail
from werkzeug.utils import secure_filename
from datetime import timedelta 
from flask_mysqldb import MySQL
from decimal import Decimal
import MySQLdb.cursors
import re
import yaml
import time
import datetime
import os
import random
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


# Set up for Emailing Forgotten Password
# Our account information:
#   EMAIL: BazarCustomerService@gmail.com;
#   PASSWORD: BazarCS316;
#   FIRST NAME: Bazar;
#   LAST NAME: Customer Service;
#   BIRTH DATE: Dec 20, 2000

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'BazarCustomerService@gmail.com'
app.config['MAIL_PASSWORD'] = 'BazarCS316'
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_MAX_EMAILS'] = 1
app.config['MAIL_DEFAULT_SENDER'] = 'BazarCustomerService@gmail.com'
mail = Mail(app)

# Set-up for image uploads
UPLOAD_FOLDER = 'static/jpg/avatars'
ALLOWED_EXTENSIONS = {'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = ALLOWED_EXTENSIONS
def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
DEFAULT_USER_AVATARS = ["apple.jpg", "cat.jpg", "chicken.jpg", "dog.jpg", "duck.jpg", "primrose.jpg"]

# Home page, renders homepage.html
@app.route("/", methods = ["POST","GET"])
def home():
    if "user" in session:
        logvar = True 
        first_name = session["first_name"]
        if request.method == "POST": # If the method that is called in homepage.html is a post method
            # Store Values from the form into searchinput variable
            searchinput = request.form["search"]
            # print(searchinput)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # This opens a cursor that can interact with the databases
            cursor.execute('SELECT name, price, avg_rating, description, image FROM Items WHERE name LIKE %s', [searchinput]) # Selects all items where searchinput matches
            searchr = cursor.fetchall() # takes all of these instances into account
            print(searchr)
            # return render_template("searchresults.html", logvar = logvar, name = searchr[0], price = searchr[1], avg_rating = searchr[2], image = searchr[3], description = searchr[4], searchr = searchr)
        return render_template("homepage.html", logvar = logvar, first_name = first_name)
    else:
        logvar = False
        return render_template("homepage.html", logvar = logvar)
#UNFINISHED, need to add matching for seller and functionality for showing results by jumping to results pagegit 

# @app.route("/searchresults", methods = ["POST","GET"])
# def search():
#     if request.method == "POST": # If the method that is called in homepage.html is a post method
#         # Store Values from the form into searchinput variable
#         searchinput = request.form["search"]
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # This opens a cursor that can interact with the databases
#         cursor.execute('SELECT name, price, avg_rating, description, image FROM Items, Category, Sellers WHERE %s LIKE Items.name OR %s LIKE Category.name OR %s LIKE Sellers.organization', [searchinput]) # Selects all items where searchinput matches
#         searchr = cursor.fetchall() # takes all of these instances into account
#         searchresults()
#     else:
#         return render_template("login.html")

# def display_recs():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('SELECT * FROM Category')
#     toprecs = cursor.fetchall()
#     return render_template('homepage.html', data = toprecs)

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
            cursor.execute('SELECT userID FROM buyers WHERE email = %s AND password = %s',(user,password))
            userID = cursor.fetchone()

            #Give email (user), password, first_name, userID variables to the session 
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
                session["org"] = seller['organization']
            else:
                session["seller"] = False
            flash("Login Successful!") # Flash a message that says login succesful 
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

# # Sends email with password to recovery email!
@app.route("/forgotpw", methods = ["POST","GET"])
def forgotpw():
    if request.method == "POST":
        recovery_email = request.form["email"]

        # Access User's Info in DB
        cursor =  mysql.connection.cursor()
        cursor.execute('SELECT email FROM buyers WHERE email = %s',[recovery_email])
        if_email_exists = cursor.fetchone()
        if(if_email_exists != recovery_email):
            flash("Whoops! No account matches this email address.")
            return redirect(url_for("registration"))
        
        cursor.execute('SELECT * FROM buyers WHERE email = %s', [recovery_email])
        user_info = cursor.fetchone()

        name = user_info[4]
        pw = user_info[2]

        msg = Message('Bazar Password Recovery', recipients = [recovery_email])
        msg.body = "Hello {}!\n\nYou recently selected the 'Forgot Password' option on our site.  Your current password is: {} .\nIf this request did not come from you, consider resetting your password on our site through your User Profile page.\n\nPlease do not reply to this email. This account is not monitored.".format(name, pw)
        mail.send(msg)
        flash("Password recovery successful. Check your email!")
        return redirect(url_for("login"))
    else:
        return render_template("forgotpw.html")

# Logout page, clears session
@app.route("/logout")
def logout():
    # notifies that you've been logged out
    flash("You have been logged out", "info") #warning, info, error
    # Pops the user info out of the session
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("home"))


# DEBUG PROFILE PICTURE DISPLAY; MODIFY DATA
@app.route("/user", methods = ["POST", "GET"])
def user():
   if "user" in session:
       logvar = True
       first_name = session["first_name"]
       last_name = session["last_name"]
       userID = session["userID"]
       seller = session["seller"]
       # Open cursor to get all details about user
       cursor = mysql.connection.cursor()
       cursor.execute('SELECT * FROM buyers WHERE userID = %s', [userID])
       # All user data stored in Buyers: (userID, email, password,
       #   currentBalance, first_name, last_name, image)
       info = cursor.fetchone()
       return render_template("user.html", logvar = logvar, first_name = first_name, last_name = last_name, balance = info[3], user = info[1], seller = seller, info = info, image_path = info[6])
   else:
       flash("You are not logged in!")
       return redirect(url_for("login"))

# DEBUG
@app.route("/registration", methods = ["POST", "GET"])
def registration():
   if "user" in session:
       flash("You are already logged in! Logout to register as different user.")
       return redirect(url_for("user"))
   elif request.method == "POST":
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
       if len(org_name) == 0: org_name = "{} {}".format(first, last)
       descr = request.form["description"]
       ifSeller = request.form.get("sellercheck")
 
       # Determine New Unique UserID
       cursor.execute('SELECT max(userID) as A FROM Buyers')
       maxID = cursor.fetchone()
       if(maxID == None): maxID = 0
       print(maxID)
       userID = maxID["A"] + 1

       # TODO: Handle avatar upload
       uploaded_file = request.files['avatar']
       filename = secure_filename(uploaded_file.filename)
       if filename != '':
           file_ext = os.path.splitext(filename)[1]
           if file_ext not in app.config['UPLOAD_EXTENSIONS']:
               abort(400)
           # Save file name as user id
           avatarID = "{}{}".format(session[userID], ".jpg")
           uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], avatarID))
           avatar_path = "{}/{}".format(UPLOAD_FOLDER, avatarID)
       else:
           avatar_path = "static/jpg/default_avatars/{}".format(random.choice(DEFAULT_USER_AVATARS))

       # Create User in Buyers
       # Buyers(userID, email, password, currentBalance, firstname, lastname, image)
       cursor.execute('INSERT INTO Buyers VALUES(%s, %s, %s, %s, %s, %s, %s)',[userID, email, password, 0.00, first, last, avatar_path])
       mysql.connection.commit()
 
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
   if "user" in session: # Check if user is logged in
      logvar = True # Update logvar boolean if so
      # Retrieve session data
      first_name = session["first_name"]
      buyerID = session["userID"]
      # Open a cursor and get items purchased from user in purchases
      cursor = mysql.connection.cursor()
      cursor.execute('SELECT itemID, name, sellerId, price, num FROM cartitems WHERE buyerID = %s', [buyerID])
      cartItems = cursor.fetchall()
      totalPrice = 0
      for row in cartItems:
          totalPrice = totalPrice + (row[3] * row[4])
      return render_template("cart.html", logvar = logvar, buyerID = buyerID, first_name = first_name, cartItems = cartItems, totalPrice = totalPrice)
   else: # If you somehow accessed this page and weren't logged in
     flash("You are not logged in to add balance")
     return redirect(url_for("home"))
 
#UPDATE CART QUANTITY
# check if sufficient seller supply
@app.route('/cart/<id>', methods = ["POST", "GET"])
def modQuantity(id):
    if "user" in session:
        if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            logvar = True
            itemID = id
            cursor.execute('SELECT num FROM cart WHERE itemID = %s', [itemID])
            currQuantity = cursor.fetchone()
            quantity = currQuantity['num']
            #find quantity available of item on seller side
            cursor.execute('SELECT num FROM items WHERE itemID = %s', [itemID])
            available = cursor.fetchone()
            supply = available['num']
            print("Supply: ", supply)
            #retrieve values from form
            addValue = Decimal(request.form['addQuantity'])
            if addValue > supply:
                flash("Insufficient number of copies of item: {} items remaining. Please remove item from cart or reduce item quantity".format(supply))
                return redirect(url_for("cart"))
            else:
                newQuantity = quantity + addValue
                print(newQuantity)
                cursor.execute('UPDATE cart SET num = %s WHERE itemID = %s', [newQuantity, itemID])
                mysql.connection.commit()
                return redirect(url_for("cart"))
    else: # If you somehow accessed this page and weren't logged in
        flash("Incorrect Payment Information")
        return redirect(url_for("home"))

# Checkout Ability successful:
# - reduce buyer balance
# - increase seller balance
# - all items in cart will be added to purchase history
# - seller history will be updated with history of seller
# - quantity of item available on seller side decreased by quantity checked OUT

# Checkout Ability unsuccesful:
# - if insufficient funds --> Flash "Insufficient Funds"
# - if seller no longer has enough supply, “Insufficient number of copies of item: 
# (current quantity of that item) items remaining. 
# Please remove item from cart or reduce item quantity”
@app.route('/cart/checkout/<id>/<price>', methods = ["POST", "GET"])
def checkSuccess(id, price):
    if "user" in session:
        if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            logvar = True
            buyerID = id
            totalPrice = price
            cursor.execute('SELECT currentBalance FROM buyers WHERE userID = %s',[buyerID])
            balance = cursor.fetchone()
            money = balance['currentBalance']
            funds = Decimal(money)
            print(funds)
            #check sufficient funds
            if funds >= Decimal(totalPrice):
                #reduce buyer balance
                remainBalance = funds - Decimal(totalPrice)
                cursor.execute('UPDATE buyers SET currentBalance = %s WHERE userID = %s', [remainBalance, buyerID])
                #address updates per item in cart
                cursor.execute('SELECT itemID, name, sellerId, price, num FROM cartitems WHERE buyerID = %s', [buyerID])
                cartItems = cursor.fetchall()
                #example row:  {'itemID': 1, 'name': 'Til There Was You', 'sellerID': 167, 'price': Decimal('6.00'), 'num': 2}
                for dataRow in cartItems:
                    print("ID: ", dataRow['itemID'])
                    itemID = dataRow['itemID']
                    sellerID = dataRow['sellerID']
                    num = dataRow['num']
                    price = dataRow['price']
                    timeFormat = '%Y-%m-%d %H:%M:%S'
                    currTime = datetime.datetime.now().strftime(timeFormat)
                    print(currTime)
                    #Purchase: buyerID, itemID, dayTime, num
                    #add item to purchase --> populate user history + seller history
                    cursor.execute('INSERT INTO purchase (buyerID, itemID, dayTime, num) VALUES (%s, %s, %s, %s)', [buyerID, itemID, currTime, num])
                    mysql.connection.commit()
                    #reduce supply of item in Item
                    cursor.execute('SELECT num FROM items WHERE itemID = %s', [itemID])
                    itemQuantity = cursor.fetchone()['num']
                    print("itemQ: ", itemQuantity)
                    newCount = itemQuantity - num
                    print("newCount = itemQ - num: ", newCount)
                    cursor.execute('UPDATE items SET num = %s WHERE itemID = %s', [newCount, itemID])
                    mysql.connection.commit()
                    #increase individual seller balance
                    cursor.execute('SELECT currentBalance FROM buyers WHERE userID = %s', [sellerID])
                    sellerBalance = cursor.fetchone()['currentBalance']
                    newSellerBalance = sellerBalance + (num*price)
                    cursor.execute('UPDATE buyers SET currentBalance = %s WHERE userID = %s', [newSellerBalance, sellerID])
                    mysql.connection.commit()
                flash("Thank you for shopping at BAZAR!")
                return redirect(url_for("cart"))
            else: #if insufficient funds
                flash("Insufficient Funds")
                return redirect(url_for("cart"))
    else: # If you somehow accessed this page and weren't logged in
        flash("Incorrect Payment Information")
        return redirect(url_for("home"))


@app.route("/item/<id>")
def item(id):
    if "user" in session: # Check if user is logged in
        logvar = True # Update logvar boolean if so
        # Retrieve session data
        first_name = session["first_name"] 
        sellerID = session["userID"]
        seller = session["seller"]
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM items WHERE itemID = %s",[id])
    items = cursor.fetchall()
    item = items[0]
    return render_template("item.html",logvar = logvar, first_name = first_name,item = item)

@app.route("/addreview")
def addreview():
    if "user" in session: # Check if user is logged in
       logvar = True # Update logvar boolean if so
       # Retrieve session data
       userID = session["userID"]
       cursor = mysql.connection.cursor()
       input_itemID = request.form["itemid"]
       input_stars = request.form["stars"]
       input_comments = request.form["body"]
       cursor.execute('INSERT INTO ItemReview VALUES(userID, input_itemID, input_stars, input_comments)')
       myReview = cursor.fetchone()
       return render_template("addreview.html", logvar = logvar, userID = myReview[0], itemID = myReview[1], input_stars = myReview[2], input_comments = myReview[3], myReview = myReview)
    else: # If you somehow accessed this page and weren't logged in
       flash("You are not logged in to add a review!")
       return redirect(url_for("home"))

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
        cursor.execute('SELECT * FROM buyers WHERE userID = %s', [sellerID])
        user = cursor.fetchall()
        org = session["org"]
        # This is where the delete function is implemented
        if request.method == "POST":
            item_id = request.form["item_id"]
            cursor.execute('DELETE FROM items WHERE itemID = %s',(item_id,))
            mysql.connection.commit() # This commits the change to the actual mysql database
            return redirect(url_for("seller"))
        return render_template("seller.html", logvar = logvar, first_name = first_name, seller = seller, items = items, user=user[0], org=org)
    else: # If you somehow accessed this page and weren't logged in
        flash("You are not logged in as a seller")
        return redirect(url_for("home"))


@app.route("/addbalance")
def addbalance():
   if "user" in session: # Check if user is logged in
       logvar = True # Update logvar boolean if so
       # Retrieve session data
       first_name = session["first_name"]
       last_name = session["last_name"]
       userID = session["userID"]
       # Open a cursor and get current balance for user
       cursor = mysql.connection.cursor()
       cursor.execute('SELECT currentBalance FROM buyers WHERE userID = %s', [userID])
       currentBalance = cursor.fetchone()
       return render_template("addbalance.html", logvar = logvar, userID = userID, first_name = first_name, last_name = last_name, currentBalance = currentBalance)
   else: # If you somehow accessed this page and weren't logged in
       flash("You are not logged in to add balance")
       return redirect(url_for("home"))

@app.route("/purchasehistory")
def purchasehistory():
   if "user" in session: # Check if user is logged in
       logvar = True # Update logvar boolean if so
       # Retrieve session data
       first_name = session["first_name"]
       buyerID = session["userID"]
       # Open a cursor and get items purchased from user in purchases
       cursor = mysql.connection.cursor()
       cursor.execute('SELECT * FROM itemhistory WHERE buyerID = %s', [buyerID])
       itemsPurchased = cursor.fetchall()
       return render_template("purchasehistory.html", logvar = logvar, buyerID = buyerID, first_name = first_name, itemsPurchased = itemsPurchased)
   else: # If you somehow accessed this page and weren't logged in
      flash("You are not logged in to add balance")
      return redirect(url_for("home"))
 
# Get Item Details
@app.route('/itempage/<id>', methods = ["POST", "GET"])
def getDetails(id):
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute('SELECT itemID, sellerID, price, num FROM items WHERE itemID = %s',[id])
   itemDetails = cursor.fetchall()
   return render_template("item.html", itemDetails = itemDetails)
 
# GET EMPLOYEE
@app.route('/update/<id>', methods =["POST","GET"])
def update(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM items WHERE itemID = %s',[id])
    item = cursor.fetchall()
    cursor.close()
    print(item)
    return render_template("modify.html", item = item)

#UPDATE BALANCE
@app.route('/addbalance/<id>', methods = ["POST", "GET"])
def modBalance(id):
    if "user" in session:
        if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            logvar = True
            userID = id
            cursor.execute('SELECT currentBalance FROM buyers WHERE userID = %s', [userID])
            currentBalance = cursor.fetchone()
            currentValue = currentBalance['currentBalance']
            #get variables from form
            first_name = session["first_name"]
            last_name = session["last_name"]
            input_fname = request.form["firstname"]
            input_lname = request.form["lastname"]
            card_number = request.form["cardnumber"]
            card_code = request.form["securitycode"]
            addValue = Decimal(request.form['addValue'])
            newValue = currentValue + addValue
            print(newValue)
            #ensure valid info
            if validCreditCard(card_number) == True and len(card_code) == 3:
                cursor.execute('UPDATE buyers SET currentBalance = %s WHERE userID = %s', [newValue, userID])
                flash('Success! Your wallet has been topped up')
                mysql.connection.commit()
                return redirect(url_for("addbalance"))
            else:
                flash("Unsuccessful transaction. Please Try Again!")
                return redirect(url_for("addbalance"))
    else: # If you somehow accessed this page and weren't logged in
        flash("Incorrect Payment Information")
        return redirect(url_for("home"))


def validCreditCard(str):
    nums = str.replace(" ", "").replace("-", "")
    return (len(nums) == 16) and nums.isdecimal()

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

@app.route('/updateuser', methods =["POST","GET"])
def updateuser():
    cursor = mysql.connection.cursor()
    userID = session["userID"]
    cursor.execute('SELECT * FROM buyers WHERE userID = %s',userID)
    userdata = cursor.fetchone()
    cursor.close()
    return render_template("modifyuser.html", first_name = userdata[4], last_name = userdata[5], email = userdata[1])

@app.route('/modifymydata', methods = ["POST","GET"])
def moduser():
    if "user" in session:
        if request.method == 'POST':
            logvar = True
            userID = session["userID"]
            cursor = mysql.connection.cursor()
            # Buyers(userID, email, password, currentBalance, first_name, last_name, image);
            newfirst = request.form['newfirst']
            newlast = request.form['newlast']
            newemail = request.form['newemail']
            newpass = request.form['newpass']
            newimage = request.files['newimage']
            filename = secure_filename(newimage.filename)
            if (len(newfirst) == 0) and (len(newlast) == 0) and (len(newemail) == 0) and (len(newpass)==0) and (len(filename)==0):
                flash('You did not change any of your user information.')
                return redirect(url_for("user"))
            if len(newfirst) != 0:
                cursor.execute('UPDATE buyers SET first_name = %s WHERE userID = %s',[newfirst, userID])
                mysql.connection.commit()
            if len(newlast) != 0:
                cursor.execute('UPDATE buyers SET last_name = %s WHERE userID = %s',[newlast, userID])
                mysql.connection.commit()
            if len(newemail) != 0:
                cursor.execute('UPDATE buyers SET email = %s WHERE userID = %s',[newemail, userID])
                mysql.connection.commit()
            if len(newpass) != 0:
                cursor.execute('UPDATE buyers SET password = %s WHERE userID = %s',[newpass, userID])
                mysql.connection.commit()
            if len(filename) != 0:
                cursor.execute('UPDATE buyers SET image = %s WHERE userID = %s',[newimage, userID])
                mysql.connection.commit()
            flash('You have successfully updated your user information!')
            return redirect(url_for("user"))
    else:
        flash("You are not logged in!")
        return redirect(url_for("home"))

@app.route('/updateorg', methods =["POST","GET"])
def updateorg():
    cursor = mysql.connection.cursor()
    userID = session["userID"]
    cursor.execute('SELECT * FROM sellers WHERE userID = %s',userID)
    orgdata = cursor.fetchone()
    cursor.close()
    return render_template("modifyorg.html", name = orgdata[1], descr = orgdata[3], image = orgdata[2])

@app.route('/modifymyorgdata', methods = ["POST","GET"])
def modorg():
    if "user" in session:
        if request.method == 'POST':
            logvar = True
            userID = session["userID"]
            cursor = mysql.connection.cursor()
            # Buyers(userID, email, password, currentBalance, first_name, last_name, image);
            newname = request.form['newname']
            newdescr = request.form['newdescr']
            newimage = request.files['newimage']
            filename = secure_filename(newimage.filename)
            if (len(newname) == 0) and (len(newdescr) == 0) and (len(filename)==0):
                flash('You did not change any of your organization information.')
                return redirect(url_for("seller"))
            if len(newname) != 0:
                cursor.execute('UPDATE sellers SET organization = %s WHERE userID = %s',[newname, userID])
                mysql.connection.commit()
            if len(newdescr) != 0:
                cursor.execute('UPDATE sellers SET description = %s WHERE userID = %s',[newdescr, userID])
                mysql.connection.commit()
            if len(filename) != 0:
                cursor.execute('UPDATE sellers SET image = %s WHERE userID = %s',[newimage, userID])
                mysql.connection.commit()
            flash('You have successfully updated your organization information!')
            return redirect(url_for("seller"))
    else:
        flash("You are not logged in!")
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

@app.route('/tradehistory', methods = ['POST','GET'])
def tradehistory():
    if "user" in session and session["seller"] == True:
        logvar = True
        first_name = session["first_name"]
        sellerID = session["userID"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM final WHERE userID = %s', [sellerID])
        history = cursor.fetchall()
        print(history)
        return render_template('tradehistory.html',logvar = logvar, first_name = first_name, history = history)
    else:
        flash("You are not logged in/a seller")
        return redirect(url_for("home"))
    




if __name__ == "__main__":
    app.run(debug=True)