from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from models import db, Feedback, Book, Customer, Order, OrderItem
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bookhub-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ініціалізація бази даних з тестовими даними
@app.before_first_request
def create_tables():
    db.create_all()
    # Додаємо тестові книги якщо їх немає
    if Book.query.count() == 0:
        sample_books = [
            Book(
                title="Хіба що хтось стукне у двері", 
                author="Стівен Кінг", 
                description="Збірник оповідань від короля жахів. 12 історій, що вражають глибиною та непередбачуваністю.",
                price=350.0, 
                category="Фантастика",
                image_url="/static/images/book1.jpg"
            ),
            Book(
                title="Проєкт 'Розі'", 
                author="Енді Вейр", 
                description="Наукова фантастика від автора 'Марсіянина'. Захоплива історія про космічні пригоди.",
                price=280.0, 
                category="Фантастика",
                image_url="/static/images/book2.jpg"
            ),
            Book(
                title="Чотири вітри", 
                author="Крістін Ханна", 
                description="Історична драма про силу родинних зв'язків у складні часи.",
                price=320.0, 
                category="Драма",
                image_url="/static/images/book3.jpg"
            ),
            Book(
                title="Гаррі Поттер і філософський камінь", 
                author="Дж. К. Роулінг", 
                description="Перша книга знаменитої серії про молодого чарівника.",
                price=290.0, 
                category="Фентезі",
                stock_quantity=15
            ),
            Book(
                title="Війна і мир", 
                author="Лев Толстой", 
                description="Класика світової літератури про долі людей під час наполеонівських воєн.",
                price=420.0, 
                category="Класика",
                stock_quantity=8
            )
        ]
        db.session.bulk_save_objects(sample_books)
        db.session.commit()
        print("Тестові книги додані до бази даних!")

# Головні маршрути
@app.route('/')
def index():
    featured_books = Book.query.filter_by(in_stock=True).limit(3).all()
    return render_template('index.html', featured_books=featured_books)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/books')
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

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        rating = int(request.form.get('rating', 5))
        
        feedback = Feedback(name=name, email=email, message=message, rating=rating)
        db.session.add(feedback)
        db.session.commit()
        flash('Дякуємо за ваш відгук! Він буде опублікований після перевірки.', 'success')
        return redirect(url_for('reviews'))
    
    approved_feedbacks = Feedback.query.filter_by(is_approved=True).order_by(Feedback.created_at.desc()).all()
    return render_template('reviews.html', feedbacks=approved_feedbacks)

# Маршрути магазину
@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    book_id_str = str(book_id)
    
    if book_id_str in cart:
        cart[book_id_str] += 1
    else:
        cart[book_id_str] = 1
    
    session['cart'] = cart
    flash('Книга додана до кошика!', 'success')
    return redirect(url_for('books'))

@app.route('/cart')
def cart():
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for book_id, quantity in session['cart'].items():
            book = Book.query.get(int(book_id))
            if book:
                item_total = book.price * quantity
                cart_items.append({
                    'book': book,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
    
    return render_template('shop/cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:book_id>', methods=['POST'])
def update_cart(book_id):
    quantity = int(request.form['quantity'])
    
    if 'cart' in session:
        cart = session['cart']
        book_id_str = str(book_id)
        
        if quantity <= 0:
            cart.pop(book_id_str, None)
        else:
            cart[book_id_str] = quantity
        
        session['cart'] = cart
        flash('Кошик оновлено!', 'success')
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Ваш кошик порожній!', 'warning')
        return redirect(url_for('books'))
    
    if request.method == 'POST':
        # Створення клієнта
        customer = Customer(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address']
        )
        db.session.add(customer)
        db.session.flush()  # Отримуємо ID клієнта
        
        # Створення замовлення
        total = 0
        cart = session['cart']
        for book_id, quantity in cart.items():
            book = Book.query.get(int(book_id))
            total += book.price * quantity
        
        order = Order(
            customer_id=customer.id,
            total_amount=total,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()
        
        # Додавання товарів до замовлення
        for book_id, quantity in cart.items():
            book = Book.query.get(int(book_id))
            order_item = OrderItem(
                order_id=order.id,
                book_id=book.id,
                quantity=quantity,
                price=book.price
            )
            db.session.add(order_item)
            
            # Оновлення кількості на складі
            book.stock_quantity -= quantity
            if book.stock_quantity <= 0:
                book.in_stock = False
        
        db.session.commit()
        
        # Очищення кошика
        session.pop('cart', None)
        
        flash(f'Замовлення #{order.id} успішно створено! Дякуємо за покупку!', 'success')
        return redirect(url_for('index'))
    
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for book_id, quantity in session['cart'].items():
            book = Book.query.get(int(book_id))
            if book:
                item_total = book.price * quantity
                cart_items.append({
                    'book': book,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
    
    return render_template('shop/checkout.html', cart_items=cart_items, total=total)

# Адмін-панель
@app.route('/admin')
def admin_dashboard():
    feedback_count = Feedback.query.count()
    book_count = Book.query.count()
    order_count = Order.query.count()
    customer_count = Customer.query.count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    pending_feedbacks = Feedback.query.filter_by(is_approved=False).count()
    
    return render_template('admin/dashboard.html', 
                         feedback_count=feedback_count,
                         book_count=book_count,
                         order_count=order_count,
                         customer_count=customer_count,
                         recent_orders=recent_orders,
                         pending_feedbacks=pending_feedbacks)

@app.route('/admin/feedback')
def admin_feedback():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin/feedback.html', feedbacks=feedbacks)

@app.route('/admin/approve_feedback/<int:feedback_id>')
def approve_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.is_approved = True
    db.session.commit()
    flash('Відгук схвалено', 'success')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/delete_feedback/<int:feedback_id>')
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Відгук видалено', 'success')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/books')
def admin_books():
    books = Book.query.all()
    return render_template('admin/books.html', books=books)

@app.route('/admin/add_book', methods=['GET', 'POST'])
def admin_add_book():
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            description=request.form['description'],
            price=float(request.form['price']),
            category=request.form['category'],
            stock_quantity=int(request.form['stock_quantity']),
            in_stock=bool(request.form.get('in_stock'))
        )
        db.session.add(book)
        db.session.commit()
        flash('Книгу додано успішно!', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/add_book.html')

@app.route('/admin/orders')
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Статус замовлення оновлено!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/customers')
def admin_customers():
    customers = Customer.query.all()
    return render_template('admin/customers.html', customers=customers)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)