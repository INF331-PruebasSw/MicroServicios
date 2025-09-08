from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///microeventos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # redirige a login si no está logueado

from routes import *

if __name__ == "__main__":
    app.run(debug=True)
