from flask import Blueprint, jsonify
from app.models import Book, Loan, Author

api_bp = Blueprint('api', __name__)

@api_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': b.id,
        'title': b.title,
        'isbn': b.isbn,
        'year': b.year,
        'quantity': b.quantity,
        'author': b.author.name
    } for b in books])

@api_bp.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'bio': a.bio
    } for a in authors])

@api_bp.route('/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    return jsonify([{
        'id': l.id,
        'user': l.borrower.username,
        'book': l.book.title,
        'issue_date': l.issue_date.isoformat(),
        'due_date': l.due_date.isoformat(),
        'is_returned': l.is_returned,
        'is_overdue': l.is_overdue
    } for l in loans])