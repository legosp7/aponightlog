from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager #potentially not needed?
import psycopg2

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
'''remove the below lines if no login needed'''
login = LoginManager(app)
login.login_view = 'login'  # Set the login view for Flask-Login

# from sqlalchemy import create_engine
# engine = create_engine('postgresql+psycopg2://span:12345@hostname/app')

# import psycopg2
# conn_string = "host='localhost' dbname='app' user='span' password='12345'"
# conn = psycopg2.connect(conn_string)


from app import routes, models

