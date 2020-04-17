#FUNCTIONALITY

* Registration with username and password.
* Login, Logout
* Imported 5000 books from books.csv (import.py)
* Search for a book by ISBN number/ the title / the author of a book. After performing the search, a list of possible matching results is displayed. It is possible to enter only part of a title, ISBN, or author name.
* Book Page contains details about the book: title, author, publication year, ISBN number, and any reviews that users have left for the book. Also provides the average rating and number of ratings the work has received from Goodreads (using their API).
* Review Submission (onn the book page) consist of a rating on a scale of 1 to 5, and text component. Users are not able to submit multiple reviews for the same book.
* API Access on a GET request to .../api/<isbn> route, where <isbn> is an ISBN number of a book.


# SELECT AVG (for jsonify)
not fetchone() but scalar() - return item
convert to float()

#THINGS TO IMPROVE
in application.py

for route /register and /login separate GET and POST methods;
make one query to related tables not several to separate tables;
add message that there where no matches if nothing was found with a search;
in search how do I arrange results so that the most matching ones are above;

in templates

On book page, improve JS notification of review submitting so that after submitting a review for the second time, it gave error message;
Make yellow stars;





