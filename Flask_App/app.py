from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
import base64
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../../database.db'
db = SQLAlchemy(app)

def user_exist(email):
    check = user.query.filter_by(email=email).first()
    if check is not None:
        return True
    return False



class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))
    mac = db.Column(db.String(120))
    pubk = db.Column(db.String(2048))

@app.route("/")
def index():
    return render_template("login.html")



@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mail = request.form["mail"]
        passw = request.form["passw"]
        
        login = user.query.filter_by(email=mail, password=passw).first()
        if login is not None:
            return render_template("main.html",email=mail,mac=login.mac)
        else:
            return render_template("login.html",error="Invalid Email and Password")

    return render_template("login.html",error="")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        mail = request.form['mail']
        passw = request.form['passw']
        mac = request.form['mac']
        pubk = request.files['pubk']

        file_data = base64.b64encode(pubk.read()).decode('utf-8')

        if user_exist(mail):
            error = "User Already Existed"
            return render_template("register.html",error=error)
        register = user(email = mail, password = passw, mac=mac,pubk=file_data)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html",error="")

with app.app_context():
    db.create_all()
    app.run(host="0.0.0.0", port=5000,debug=True)