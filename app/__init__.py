'''
NAME:    __init__.py - Initializes the Flask application and its extensions.
PURPOSE: Sets up the Flask app, configures it, and initializes extensions like SQLAlchemy, Migrate, and Mail. 
Also configures error logging to email administrators and log to a file.

'''


from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#below for error emailing
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail

import psycopg2


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

def create_app(config_class=Config) -> Flask:
    '''
    Factory function to create and configure the Flask application.
    Args:
        config_class: The configuration class to use for the app (default is Config).
    Returns:
        A configured Flask application instance.
    
    '''
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    if not app.debug:
        #this part is just for error logging to email and file when not in debug mode
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Nightlog App Failure',
                credentials=auth, secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nightlog_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        # Create a file handler for logging
        app.logger.info('Nightlog App Startup')
    
    return app
            



# Register the error handlers to email errors

        
from app import models, autofill






