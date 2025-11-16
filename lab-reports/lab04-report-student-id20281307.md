# Звіт з лабораторної роботи 4

## Реалізація бази даних для вебпроєкту

### Інформація про команду
- Назва команди: **Ardoes**

- Учасники:
  - Дмитерчук Віталій Вадимович (full-stack розробник)

## Завдання

### Обрана предметна область

**Книжкова спільнота "BookHub" з функціоналом інтернет-магазину**
Веб-застосунок дозволяє користувачам переглядати книги, залишати відгуки, купувати книги через інтернет-магазин. Адміністратор може керувати книгами, замовленнями, відгуками та клієнтами через адмін-панель.

### Реалізовані вимоги

Вкажіть, які рівні завдань було виконано:

- [+] Рівень 1: Створено базу даних SQLite з таблицею для відгуків, реалізовано базові CRUD операції, створено адмін-панель для перегляду та видалення відгуків, додано функціональність магазину з таблицями для товарів та замовлень
- [+] Рівень 2: Створено додаткову таблицю, релевантну предметній області, реалізовано роботу з новою таблицею через адмін-панель, інтегровано функціональність у застосунок
- [+] Рівень 3: Розширено функціональність двома додатковими функціями, що суттєво покращують користувацький досвід

## Хід виконання роботи

### Підготовка середовища розробки

Опишіть процес налаштування:

- **Версія Python**: 3.14.0
- **Встановлені бібліотеки**: Flask==3.1.2, Flask-SQLAlchemy==3.1.1, Flask-WTF==1.2.2, WTForms==3.2.1
- **База даних**: SQLite
- **Інші інструменти**: Visual Studio Code, Git, GitHub Desktop

### Структура проєкту

Наведіть структуру файлів та директорій вашого проєкту:

```
LAB3-4-FLASK-WEBAPP/
├── .pytest_cache/                          # Кеш тестування (автоматично)
│   └── ...
├── .venv/                                  # Віртуальне середовище Python
│   ├── Scripts/
│   ├── Include/
│   └── Lib/
├── instance/                               # Папка екземпляра Flask
│   └── bookhub.db                          # База даних SQLite (автоматично)
├── lab-reports/                            # Звітна документація
│   ├── about.png                           # Скріншот сторінки "Про нас"
│   ├── admin.png                           # Скріншот адмін-панелі
│   ├── books.png                           # Скріншот каталогу книг
│   ├── cart.png                            # Скріншот кошика
│   ├── home.png                            # Скріншот головної сторінки
│   ├── lab04-report-student-id20281307     # Звіт лабораторної роботи 4
│   ├── order.png                           # Скріншот керування замовленнями
│   └── reviews.png                         # Скріншот сторінки відгуків
├── templates/                              # HTML шаблони
│   ├── admin/                              # Адмін-панель
│   │   ├── add_book.html                   # Додавання нової книги
│   │   ├── books.html                      # Управління книгами
│   │   ├── customers.html                  # Управління клієнтами
│   │   ├── dashboard.html                  # Головна адмін-панель
│   │   ├── feedback.html                   # Управління відгуками
│   │   └── orders.html                     # Управління замовленнями
│   ├── shop/                               # Магазин
│   │   ├── cart.html                       # Кошик покупок
│   │   └── checkout.html                   # Оформлення замовлення
│   ├── about.html                          # Сторінка "Про нас"
│   ├── base.html                           # Базовий шаблон
│   ├── books.html                          # Каталог книг (з пошуком)
│   ├── index.html                          # Головна сторінка
│   └── reviews.html                        # Відгуки (з вибором книг)
├── .gitattributes                          # Налаштування Git
├── app.py                                  # Основний файл Flask додатка
├── models.py                               # Моделі бази даних
├── README.md                               # Документація проєкту
└── requirements.txt                        # Залежності Python
```

### Проектування бази даних

#### Схема бази даних

Опишіть структуру вашої бази даних:

```
Таблиця "feedback":
id (INTEGER, PRIMARY KEY)
name (TEXT, NOT NULL)
email (TEXT)
message (TEXT, NOT NULL)
rating (INTEGER, DEFAULT 5)
book_id (INTEGER, FOREIGN KEY) - зв'язок з книгою
created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
is_approved (BOOLEAN, DEFAULT FALSE)

Таблиця "book":
id (INTEGER, PRIMARY KEY)
title (TEXT, NOT NULL)
author (TEXT, NOT NULL)
description (TEXT)
price (REAL, NOT NULL)
image_url (TEXT)
category (TEXT)
in_stock (BOOLEAN, DEFAULT TRUE)
stock_quantity (INTEGER, DEFAULT 10)
created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

Таблиця "customer":
id (INTEGER, PRIMARY KEY)
name (TEXT, NOT NULL)
email (TEXT, NOT NULL, UNIQUE)
phone (TEXT)
address (TEXT)
created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

Таблиця "order":
id (INTEGER, PRIMARY KEY)
customer_id (INTEGER, FOREIGN KEY)
total_amount (REAL, NOT NULL)
status (TEXT, DEFAULT 'pending')
created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

Таблиця "order_item":
id (INTEGER, PRIMARY KEY)
order_id (INTEGER, FOREIGN KEY)
book_id (INTEGER, FOREIGN KEY)
quantity (INTEGER, NOT NULL)
price (REAL, NOT NULL)
```


### Опис реалізованої функціональності

#### Система відгуків

Реалізовано розширену систему відгуків, де користувачі можуть залишати відгуки як про конкретні книги, так і про магазин в цілому. Відгуки проходять модерацію адміністратора перед публікацією. Адміністратор може схвалювати або видаляти відгуки через адмін-панель.

#### Магазин

Реалізовано повний цикл покупки:
- **Каталог книг**: відображення всіх книг з можливістю пошуку за назвою/автором та фільтрації за категоріями
- **Кошик**: додавання книг до кошика, оновлення кількості, видалення товарів
- **Оформлення замовлення**: форма з введенням даних клієнта, автоматичне створення запису про клієнта
- **Адмін-панель для управління товарами**: додавання нових книг, перегляд списку книг, контроль запасів

#### Адміністративна панель

Адмін-панель включає повний контроль над сайтом:
- **Дашборд**: статистика по книгам, відгукам, замовленням, клієнтам
- **Управління відгуками**: перегляд, схвалення, видалення відгуків
- **Управління книгами**: перегляд списку книг, додавання нових книг
- **Управління замовленнями**: перегляд замовлень, зміна статусу замовлення
- **Управління клієнтами**: перегляд списку клієнтів та їхніх замовлень

#### Додаткова функціональність (якщо реалізовано)

- **Система клієнтів**: автоматичне створення запису про клієнта при оформленні замовлення, зберігання історії замовлень, перегляд клієнтів в адмін-панелі
- **Пошук та фільтрація книг**: пошук за назвою та автором, фільтрація за категоріями, зручний інтерфейс для користувачів

## Ключові фрагменти коду

### Ініціалізація бази даних

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    book = db.relationship('Book', backref=db.backref('feedbacks', lazy=True))
```

### CRUD операції

Наведіть приклади реалізації CRUD операцій:

#### Створення (Create)

``` @app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        rating = int(request.form.get('rating', 5))
        book_id = request.form.get('book_id')
        
        feedback = Feedback(
            name=name, email=email, message=message, 
            rating=rating, book_id=book_id if book_id else None
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Дякуємо за ваш відгук! Він буде опублікований після перевірки.', 'success')
        return redirect(url_for('reviews'))
```

#### Читання (Read)

``` @app.route('/admin/feedback')
def admin_feedback():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin/feedback.html', feedbacks=feedbacks)
```

#### Оновлення (Update)

``` @app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Статус замовлення оновлено!', 'success')
    return redirect(url_for('admin_orders'))
```

#### Видалення (Delete)

``` @app.route('/admin/delete_feedback/<int:feedback_id>')
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Відгук видалено', 'success')
    return redirect(url_for('admin_feedback'))
```

### Маршрутизація

Наведіть приклади маршрутів для роботи з базою даних:

``` @app.route('/books')
def books():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Book.query.filter_by(in_stock=True)
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    
    books = query.all()
    categories = db.session.query(Book.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('books.html', books=books, categories=categories, selected_category=category, search_query=search)
```

### Робота зі зв'язками між таблицями

Наведіть приклад запиту з використанням JOIN для отримання пов'язаних даних:

``` class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    book = db.relationship('Book', backref=db.backref('order_items', lazy=True))
```

## Розподіл обов'язків у команді

Оскільки я працював самостійно, то виконав всі завдання:

Дмитерчук Віталій Вадимович: проектування бази даних, створення моделей, реалізація CRUD операцій, створення маршрутів, розробка шаблонів, адмін-панель, система відгуків, інтернет-магазин, пошук та фільтрація, тестування, документація.

## Скріншоти

Додайте скріншоти основних функцій вашого вебзастосунку:

### Форма зворотного зв'язку

![Форма зворотного зв'язку]
https://github.com/Armovolt/lab3-4-flask-webapp/blob/875b4c0c04bbf19e14e21c1bf7be4ee10106d639/lab-reports/reviews.png

### Каталог товарів

![Каталог товарів]
https://github.com/Armovolt/lab3-4-flask-webapp/blob/875b4c0c04bbf19e14e21c1bf7be4ee10106d639/lab-reports/books.png

### Адміністративна панель

![Адмін-панель]
https://github.com/Armovolt/lab3-4-flask-webapp/blob/875b4c0c04bbf19e14e21c1bf7be4ee10106d639/lab-reports/admin.png

### Управління замовленнями

![Управління замовленнями]


### Додаткова функціональність

![Додаткова функція]


## Тестування

### Сценарії тестування

Опишіть, які сценарії ви тестували:

1. Додавання нового відгуку та перевірка його відображення в адмін-панелі
2. Створення товару, додавання його до кошика та оформлення замовлення
3. Зміна статусу замовлення через адмін-панель
4. Видалення записів з бази даних
5. Перевірка валідації даних


## Висновки

Опишіть:

Що вдалося реалізувати успішно:
- Повнофункціональну базу даних SQLite з 5 таблицями та правильними зв'язками
- CRUD операції для всіх основних сутностей (відгуки, книги, клієнти, замовлення)
- Адмін-панель для повного управління даними
- Інтернет-магазин з кошиком та оформленням замовлень
- Систему клієнтів з автоматичною реєстрацією та історією замовлень
- Пошук та фільтрацію книг за назвою, автором та категоріями
- Розширену систему відгуків з можливістю залишати відгуки про конкретні книги

Які навички роботи з базами даних отримали:
- Робота з Flask-SQLAlchemy для ORM та управління базою даних
- Проектування схем бази даних з зв'язками між таблицями
- Реалізація CRUD операцій для веб-застосунків
- Створення адміністративних інтерфейсів для управління даними
- Робота з сесіями для реалізації кошика покупок
- Впровадження пошуку та фільтрації даних

Які труднощі виникли при проектуванні схеми БД:
- Налаштування зв'язків між таблицями та правильне використання foreign keys
- Організація коду для великої кількості маршрутів та функцій
- Валідація даних у формах та обробка помилок
- Вирішення конфліктів середовищ Python при запуску додатка

Як організували командну роботу:
Оскільки робота виконувалась індивідуально, весь проєкт було реалізовано самостійно, що
дозволило повністю контролювати архітектуру та реалізацію.

Які покращення можна внести в майбутньому:
- Додати авторизацію користувачів з різними ролями
- Реалізувати пагінацію для великих списків
- Додати більше валідації даних та обробку помилок
- Покращити дизайн та UX адмін-панелі
- Додати email сповіщення про нові замовлення
- Реалізувати систему знижок та промокодів

Очікувана оцінка: [4-12 балів]

Обґрунтування: Виконано всі вимоги трьох рівнів завдання. Реалізовано базу даних з 5 таблицями та зв'язками, CRUD операції для всіх сутностей, адмін-панель для управління даними, інтернет-магазин з кошиком та замовленнями, систему клієнтів з автоматичною реєстрацією, пошук та фільтрацію книг, розширену систему відгуків з можливістю залишати відгуки про конкретні книги. Проєкт завантажено на GitHub, підготовлено детальний звіт, додаток повністю функціональний та готовий до використання.