from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes at the bottom to avoid circular import issues
from app.auth import routes