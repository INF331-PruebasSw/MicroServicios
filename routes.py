from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from models import User, Event, Transaction
import datetime

# -------------------- LOGIN MANAGER --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- HOME --------------------
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    query = Event.query
    category = request.args.get('category')
    if category:
        query = query.filter(Event.category.ilike(f"%{category}%"))
    search = request.args.get('search')
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))
    events = query.order_by(Event.date).all()

    total_eventos = len(events)
    total_cupos = sum(event.capacity for event in events)
    eventos_agotados = [event for event in events if event.capacity == 0]
    return render_template(
        'home.html',
        events=events,
        search=search,
        category=category,
        total_eventos=total_eventos,
        total_cupos=total_cupos,
        eventos_agotados=eventos_agotados
    )

# -------------------- LOGIN --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Bienvenido {user.username}!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Email o contraseña incorrectos", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

# -------------------- REGISTER --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# -------------------- LOGOUT --------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# -------------------- LIST EVENTS --------------------
@app.route('/events')
@login_required
def events_list():
    events = Event.query.all()
    return render_template('events_list.html', events=events)

# -------------------- CREATE EVENT --------------------
@app.route('/event/new', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        location = request.form.get('location')
        category = request.form.get('category')
        try:
            price = int(request.form.get('price'))
            capacity = int(request.form.get('capacity'))
        except ValueError:
            flash('Precio o capacidad inválidos.', 'danger')
            return redirect(url_for('create_event'))
        try:
            event_date = datetime.datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Formato de fecha/hora inválido.', 'danger')
            return redirect(url_for('create_event'))
        event = Event(
            title=title,
            description=description,
            date=event_date,
            location=location,
            category=category,
            price=price,
            capacity=capacity,
            creator=current_user
        )
        db.session.add(event)
        db.session.commit()
        flash('Evento creado exitosamente!', 'success')
        return redirect(url_for('home'))
    return render_template('create_event.html')

# -------------------- VIEW EVENT --------------------
@app.route('/event/<int:event_id>')
@login_required
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('view_event.html', event=event)


# -------------------- EDIT EVENT --------------------
@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title', event.title)
        event.description = request.form.get('description', event.description)
        event.location = request.form.get('location', event.location)
        event.category = request.form.get('category', event.category)
        price_str = request.form.get('price')
        capacity_str = request.form.get('capacity')
        try:
            event.price = int(price_str)
            event.capacity = int(capacity_str)
        except (TypeError, ValueError):
            flash('Precio o capacidad inválidos.', 'danger')
            return redirect(url_for('edit_event', event_id=event.id))

        datetime_str = request.form.get('date')
        try:
            event.date = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
        except (TypeError, ValueError):
            flash('Formato de fecha/hora inválido.', 'danger')
            return redirect(url_for('edit_event', event_id=event.id))

        try:
            db.session.commit()
            flash('Evento actualizado exitosamente!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el evento: {e}', 'danger')
            return redirect(url_for('edit_event', event_id=event.id))

    return render_template('edit_event.html', event=event)


# -------------------- DELETE EVENT --------------------
@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Evento eliminado exitosamente!', 'success')
    return redirect(url_for('home'))

# -------------------- VENDER TICKET --------------------
@app.route('/event/<int:event_id>/sell', methods=['POST'])
@login_required
def sell_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    quantity = int(request.form.get('quantity', 0))
    if quantity <= 0 or quantity > event.capacity:
        flash("Cantidad inválida.", "danger")
        return redirect(url_for('view_event', event_id=event.id))
    transaction = Transaction(event_id=event.id, type='venta', quantity=quantity)
    db.session.add(transaction)
    event.capacity -= quantity
    db.session.commit()
    flash(f"Se vendieron {quantity} entradas para {event.title}.", "success")
    return redirect(url_for('view_event', event_id=event.id))

# -------------------- DEVOLVER TICKET --------------------
@app.route('/event/<int:event_id>/return', methods=['POST'])
@login_required
def return_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    quantity = int(request.form.get('quantity', 0))
    if quantity <= 0:
        flash("Cantidad inválida.", "danger")
        return redirect(url_for('view_event', event_id=event.id))
    transaction = Transaction(event_id=event.id, type='devolucion', quantity=quantity)
    db.session.add(transaction)
    event.capacity += quantity
    db.session.commit()

    flash(f"Se devolvieron {quantity} entradas de {event.title}.", "success")
    return redirect(url_for('view_event', event_id=event.id))