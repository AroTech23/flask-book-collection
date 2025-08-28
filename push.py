from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
import os


"""
📌 Notes / Setup Guide
----------------------
- When doing any CRUD operation with SQLAlchemy:
  - `.scalar()` → returns a single object from a query (unwraps from tuple).
  - `.scalars()` → returns multiple objects.

- If you see red underlines in PyCharm (missing imports):
  On Windows:
      python -m pip install -r requirements.txt
  On MacOS:
      pip3 install -r requirements.txt

- The variable __file__ contains the path of the current script.
  Example: /Users/ngongarnold/Downloads/day-63-starting-files-library-project/main.py
"""

# ----------------------
# Database configuration
# ----------------------

# Ensure database file is always stored in the same folder as this script
db_path = os.path.join(os.path.dirname(__file__), 'new-book-collection.db')


# SQLAlchemy base class
class Base(DeclarativeBase):
    pass


# Create the SQLAlchemy extension
db = SQLAlchemy(model_class=Base)

# Initialize Flask app
app = Flask(__name__)

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Link the database to the Flask app
db.init_app(app)


# ----------------------
# Database Model
# ----------------------

class Books(db.Model):
    """
    A table to store book records
    Columns:
      - id: Primary key
      - title: Book title
      - author: Author name
      - rating: Rating given to the book
    """
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


# Create the database tables (only once when app starts)
with app.app_context():
    db.create_all()


# ----------------------
# Routes
# ----------------------

@app.route('/')
def home():
    """Home page → Shows all books in the collection"""
    result = db.session.execute(db.select(Books).order_by(Books.id))
    all_results = result.scalars().all()
    return render_template('index.html', all_books=all_results)


@app.route("/add", methods=['POST', 'GET'])
def add():
    """Add a new book to the collection"""
    if request.method == 'POST':
        # Get user input from the form
        new_dict = {
            "title": request.form.get('title', False),
            "author": request.form.get('author', False),
            "rating": request.form.get('rating', False)
        }

        # Create a new book object
        new_book = Books(
            title=new_dict['title'],
            author=new_dict['author'],
            rating=float(new_dict['rating'])
        )

        # Add to the database
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add.html')


@app.route("/edit", methods=['POST', 'GET'])
def change_rating():
    """Edit (update) the rating of a specific book"""
    id = request.args.get('id')
    table = db.get_or_404(Books, id)

    table_title = table.title
    table_rating = table.rating

    if request.method == 'POST':
        new_rating = request.form['number']

        # Update the rating of the selected book
        result = db.session.execute(
            db.select(Books).where(Books.id == id)
        ).scalar()

        result.rating = float(new_rating)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template(
        'Edit.html',
        id=id,
        table_rating=table_rating,
        table_title=table_title
    )


@app.route("/delete")
def delete():
    """Delete a book from the collection"""
    book_id = request.args.get('id')

    # Find and delete the book
    row_to_delete = db.get_or_404(Books, book_id)
    db.session.delete(row_to_delete)
    db.session.commit()

    # Flask automatically provides an app context for requests
    return redirect(url_for('home'))


# ----------------------
# Run the App
# ----------------------

if __name__ == "__main__":
    app.run(debug=True)
