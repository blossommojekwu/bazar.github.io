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

@app.route("/account")
def account():
    return render_template("profilepage.html")

@app.route("/account/seller", methods =['GET', 'POST'])
def seller():
    if request.method == 'POST':
        #Fetch form data
        marketDetails = request.form
        item = marketDetails['item']
        price = marketDetails['price']
        quantity = marketDetails['quantity']
        seller = marketDetails['seller']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO market(item, price, quantity, seller) VALUES(%s, %s, %s, %s)", (item, price, quantity, seller))
        mysql.connection.commit()
        cur.close()
        #return redirect('/display')
    return render_template("seller_items.html")


@app.route('/display')
def display():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM market")
    if resultValue > 0:
        marketDetails = cur.fetchall()
        return render_template('market.html',marketDetails = marketDetails)
    
if __name__ == "__main__":
    app.run(debug=True)