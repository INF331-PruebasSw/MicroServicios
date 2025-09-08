from flask import render_template, request, redirect, url_for, flash
from app import app, db, login_manager
from models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hhashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password=hhashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Usuario registrado correctamente")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Hola {current_user.username}, bienvenido al dashboard."

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


