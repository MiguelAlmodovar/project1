import os
import requests


from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():
    session['user_id']=[]
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "a3SL5feToB698hUq6MVSmg", "isbns": "9781632168146"})
    print(res.json())
    return render_template("index.html")

@app.route("/dashboard", methods = ["POST"])
def signin():
    name = str(request.form.get("user"))
    password = str(request.form.get("password"))
    if db.execute("SELECT * FROM users1 WHERE id = :name AND password = :password", {"name": name, "password": password}).rowcount == 0:
        return render_template("error.html", message = "Invalid credentials")
    else:
        session['user_id'] = name
    return render_template("dashboard.html",user_id = name)

@app.route("/signup")
def register():
    return render_template("signup.html")

@app.route("/dashboardaftersignup", methods = ["POST"])
def signup():
    name = str(request.form.get("user"))
    password = str(request.form.get("password"))
    if db.execute("Select * FROM users1 WHERE id = :name", {"name":name}).rowcount == 1:
        return render_template("signup.html",message = "Username already taken!")
    else:
        db.execute("INSERT INTO users1 (id, password) VALUES (:name, :password)",{"name": name, "password": password})
        db.commit()
        print(f"Added {name} to users")
        session['user_id'] = name
        return render_template("dashboard.html",user_id = name)


@app.route("/search", methods = ["POST"])
def search():
    straux = '%'
    searchinput = str(request.form.get("search")) + straux
    print(searchinput)
    buks = db.execute("SELECT isbn, title , author, year FROM buks WHERE isbn LIKE :searchinput OR title LIKE :searchinput", {"searchinput":searchinput}).fetchall()
    print(buks)
    return render_template("searchresults.html", buks = buks)
