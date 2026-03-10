'''
Name: nightlog.py
Purpose: This script initializes the Flask application and provides a shell context for interactive use.
This allows developers to easily access the application, database, and other components 
in a Python shell for testing and debugging purposes.'''

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Provide a shell context with the app, db, User, and Post models."""
    return {'sa': sa,
            'so': so,
            'db': db,
            }