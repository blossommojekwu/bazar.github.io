from flask import Flask, render_template, request, redirect      
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

# Configure db
db = yaml.load(open('./templates/db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/user")
def user():
    return render_template("user.html")

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

@app.route("/seller")
def seller():
    return render_template("seller.html")

@app.route("/addbalance")
def addbalance():
    return render_template("addbalance.html")

@app.route("/purchasehistory")
def purchasehistory():
    return render_template("purchasehistory.html")

@app.route("/tradehistory")
def tradehistory():
    return render_template("tradehistory.html")

@app.route("/sellinglist")
def sellinglist():
    return render_template("sellinglist.html")


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