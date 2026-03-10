from flask import render_template
from app import db
from app.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    """Render a custom 404 error page."""
    return render_template('/errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """Render a custom 500 error page."""
    db.session.rollback()
    return render_template('/errors/.html'), 500