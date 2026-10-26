from app import create_app, db
from app.models import User, Author, Book

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Инициализация БД и добавление тестовых данных."""
    db.drop_all()
    db.create_all()

    # Админ и обычный пользователь
    admin = User(username='admin', email='admin@mail.com', role='admin')
    admin.set_password('admin123')
    
    user = User(username='student', email='student@mail.com', role='user')
    user.set_password('user123')

    # Авторы
    a1 = Author(name='Абай Кунанбаев', bio='Великий казахский поэт, композитор, просветитель.')
    a2 = Author(name='Мухтар Ауэзов', bio='Выдающийся казахский писатель и драматург.')

    db.session.add_all([admin, user, a1, a2])
    db.session.commit()

    # Книги
    b1 = Book(title='Слова назидания', isbn='978-1234567890', year=1904, quantity=3, author_id=a1.id)
    b2 = Book(title='Путь Абая', isbn='978-0987654321', year=1942, quantity=2, author_id=a2.id)

    db.session.add_all([b1, b2])
    db.session.commit()

    print("База данных успешно инициализирована тестовыми данными!")

if __name__ == '__main__':
    app.run(debug=True)