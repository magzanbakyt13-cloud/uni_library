import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Book, Author, Loan
from app.forms import BookForm
from datetime import datetime

books_bp = Blueprint('books', __name__)

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.', 'danger')
            return redirect(url_for('books.list_books'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@books_bp.route('/')
def list_books():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')

    query = Book.query.join(Author)

    if search_query:
        query = query.filter(Book.title.ilike(f'%{search_query}%') | Author.name.ilike(f'%{search_query}%'))

    if sort_by == 'year':
        query = query.order_by(Book.year.desc())
    else:
        query = query.order_by(Book.title.asc())

    pagination = query.paginate(page=page, per_page=5, error_out=False)
    books = pagination.items

    return render_template('books/list.html', books=books, pagination=pagination, search_query=search_query, sort_by=sort_by)

@books_bp.route('/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', book=book)

@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = BookForm()
    form.author_id.choices = [(a.id, a.name) for a in Author.query.all()]
    
    if form.validate_on_submit():
        filename = None
        if form.cover.data:
            file = form.cover.data
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        book = Book(
            title=form.title.data,
            isbn=form.isbn.data,
            year=form.year.data,
            quantity=form.quantity.data,
            author_id=form.author_id.data,
            cover_image=filename
        )
        db.session.add(book)
        db.session.commit()
        flash('Книга успешно добавлена!', 'success')
        return redirect(url_for('books.list_books'))

    return render_template('books/form.html', form=form, title="Добавить книгу")

@books_bp.route('/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    form.author_id.choices = [(a.id, a.name) for a in Author.query.all()]

    if form.validate_on_submit():
        if form.cover.data:
            file = form.cover.data
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            book.cover_image = filename

        book.title = form.title.data
        book.isbn = form.isbn.data
        book.year = form.year.data
        book.quantity = form.quantity.data
        book.author_id = form.author_id.data
        db.session.commit()
        flash('Данные книги обновлены.', 'success')
        return redirect(url_for('books.detail', book_id=book.id))

    return render_template('books/form.html', form=form, title="Редактировать книгу")

@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Книга успешно удалена.', 'info')
    return redirect(url_for('books.list_books'))

@books_bp.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow(book_id):
    book = Book.query.get_or_404(book_id)
    if book.quantity <= 0:
        flash('К сожалению, этой книги нет в наличии.', 'warning')
        return redirect(url_for('books.detail', book_id=book.id))

    active_loan = Loan.query.filter_by(user_id=current_user.id, book_id=book.id, is_returned=False).first()
    if active_loan:
        flash('Вы уже взяли эту книгу.', 'warning')
        return redirect(url_for('books.detail', book_id=book.id))

    book.quantity -= 1
    loan = Loan(user_id=current_user.id, book_id=book.id)
    db.session.add(loan)
    db.session.commit()
    flash('Вы успешно взяли книгу!', 'success')
    return redirect(url_for('books.my_loans'))

@books_bp.route('/return/<int:loan_id>', methods=['POST'])
@login_required
def return_book(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.user_id != current_user.id and not current_user.is_admin:
        flash('Доступ запрещен.', 'danger')
        return redirect(url_for('main.index'))

    loan.is_returned = True
    loan.return_date = datetime.utcnow()
    loan.book.quantity += 1
    db.session.commit()
    flash('Книга успешно возвращена!', 'success')
    return redirect(url_for('books.my_loans'))

@books_bp.route('/my-loans')
@login_required
def my_loans():
    if current_user.is_admin:
        loans = Loan.query.order_by(Loan.issue_date.desc()).all()
    else:
        loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.issue_date.desc()).all()
    return render_template('loans/list.html', loans=loans)