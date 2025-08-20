import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db

@app.shell_context_processor
def make_shell_context():
    """Provide a shell context with the app, db, User, and Post models."""
    return {'sa': sa,
            'so': so,
            'db': db,
            }