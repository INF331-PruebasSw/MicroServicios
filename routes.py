from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Event

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard (vista principal)
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Obtener eventos
    upcoming_events = Event.query.filter(Event.is_sold_out == False).order_by(Event.date.asc()).all()
    sold_out_events = Event.query.filter(Event.is_sold_out == True).order_by(Event.date.desc()).all()
    return render_template('dashboard.html', upcoming_events=upcoming_events, sold_out_events=sold_out_events)

# Crear un nuevo evento
@app.route('/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        total_tickets = int(request.form['total_tickets'])
        # Considera agregar un campo para la fecha
        
        new_event = Event(name=name, description=description, total_tickets=total_tickets)
        db.session.add(new_event)
        db.session.commit()
        flash('Evento creado con éxito.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('new_event.html')

# Vender una entrada
@app.route('/event/<int:event_id>/sell', methods=['POST'])
@login_required
def sell_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    if event.sold_tickets < event.total_tickets:
        event.sold_tickets += 1
        if event.sold_tickets == event.total_tickets:
            event.is_sold_out = True
        db.session.commit()
        flash(f'Entrada vendida para {event.name}.', 'success')
    else:
        flash(f'El evento {event.name} ya está agotado.', 'danger')
    return redirect(url_for('dashboard'))

# Devolver una entrada
@app.route('/event/<int:event_id>/refund', methods=['POST'])
@login_required
def refund_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    if event.sold_tickets > 0:
        event.sold_tickets -= 1
        event.is_sold_out = False # Si devuelves una, deja de estar agotado
        db.session.commit()
        flash(f'Entrada devuelta para {event.name}.', 'success')
    else:
        flash(f'No hay entradas vendidas para {event.name} para devolver.', 'danger')
    return redirect(url_for('dashboard'))

# Es necesario un usuario inicial para poder iniciar sesión. Puedes agregarlo manualmente a la base de datos o crear una ruta de registro temporal.
# Ejemplo de creación de usuario en un script separado (no en la aplicación principal)
# from app import app, db
# from models import User
# with app.app_context():
#    user = User(username='admin')
#    user.set_password('admin123')
#    db.session.add(user)
#    db.session.commit()
#    print('Usuario admin creado.')