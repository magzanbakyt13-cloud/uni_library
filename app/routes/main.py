from flask import Blueprint, render_template
from app.models import Book, Loan, Author

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    total_books = Book.query.count()
    total_authors = Author.query.count()
    active_loans = Loan.query.filter_by(is_returned=False).count()
    return render_template('index.html', total_books=total_books, total_authors=total_authors, active_loans=active_loans)