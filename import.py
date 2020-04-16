import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	file = open('books.csv')
	reader = csv.reader(file)
	db.execute("CREATE TABLE books (id serial primary key, ISBN text not null, title varchar not null, author varchar not null, year text not null)")
	row_count = 0
	for isbn, title, author, year in reader:
		db.execute("INSERT INTO books (ISBN, title, author, year) VALUES (:isbn, :title, :author, :year)", {'isbn': isbn, 'title': title, 'author': author, 'year': year})
		row_count += 1
		print(row_count)

	db.commit()
	print(f"Added {row_count} books")

	

if __name__ == "__main__":
	main()