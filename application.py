import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, escape
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = 'riwudmsk'

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
	if 'user_id' in session:
		user_id = session['user_id']
		username = db.execute("SELECT username FROM users WHERE id = :user_id", {"user_id":user_id}).fetchone()
		return render_template("index.html", username = username)
	
	return render_template("login_error.html", message = "You are not logged in", link = "Log in")

@app.route("/register", methods=["GET","POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	username = request.form.get("username")
	password = request.form.get("password")
	db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})

	db.commit()

	return render_template("success.html")

@app.route("/login", methods=["GET","POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	if request.method == "POST":
		username = request.form.get("login_username")
		password = request.form.get("login_password")

		#make sure this pair exists:
		user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",{"username":username, "password":password}).fetchone()
		if user == None:
			return render_template("login_error.html", message = "Wrong username or password, try again", link = "Back to log in")
		#if exists, create session:
		user_id = user[0]
		session['user_id'] = user_id
	
		return redirect(url_for("index"))

@app.route("/logout")
def logout():
	#clears session:
	session.pop('user_id', None)

	return redirect(url_for('index'))
	
@app.route("/search", methods=["POST"])
def search():
	search = str(request.form.get("search"))
	result = db.execute("SELECT * FROM books WHERE UPPER(title) LIKE UPPER(:search) OR UPPER(ISBN) LIKE UPPER(:search) or UPPER(author) LIKE UPPER(:search)", {"search":'%'+search+'%'}).fetchall()
	if result == None:
		return render_template("error.html", message = "Book not found", link_message = "Go back to search")

	return render_template("search_results.html", result=result)

@app.route("/book/<book_isbn>")
def book(book_isbn): 
	KEY = "3AInDel8lhl9PJK1DNHw"
	book_data = db.execute("SELECT * FROM books WHERE ISBN = :book_isbn", {"book_isbn":book_isbn}).fetchone()

	#goodreads ratings
	res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":KEY,"isbns":book_isbn})
	if res.status_code != 200:
		raise Exception("Error: API request unsuccessful.")
	data = res.json()
	rating_count = data["books"][0]["work_ratings_count"]
	rating = data["books"][0]["average_rating"]
	rating_int=int(float(rating))

	#user's reviews for this book
	user_review = db.execute("SELECT * FROM reviews WHERE books_isbn = :book_isbn AND users_id = :user_id", {"book_isbn":book_isbn,"user_id":session['user_id']}).fetchone()
	#other users' reviews for this book
	other_reviews = db.execute("SELECT * FROM reviews WHERE books_isbn = :book_isbn", {"book_isbn":book_isbn}).fetchall()

	return render_template("book.html", book_data=book_data, rating_count=rating_count, rating=rating, rating_int=rating_int,user_review=user_review,other_reviews=other_reviews)

@app.route("/add_review", methods=["POST"])
def add_review():
	review = request.form.get("review")
	rating = request.form.get("review_rating")
	user_id = session["user_id"]
	books_isbn = request.form.get("book_isbn")

	#check if there is already review for this book from this user:
	if db.execute("SELECT * FROM reviews WHERE books_isbn = :books_isbn AND users_id = :user_id",{"books_isbn":books_isbn,"user_id":user_id}).rowcount != 0:
		return render_template("error.html", message = "You already subbmited a review for this book", link_message = "Back to book page", book_isbn=books_isbn)
	db.execute("INSERT INTO reviews (review, books_isbn, users_id, rating) VALUES (:review, :books_isbn, :user_id, :rating)",{"review":review,"books_isbn":books_isbn,"user_id":user_id,"rating":rating})
	db.commit()

	return redirect(url_for("book",book_isbn=books_isbn))


