from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import routes after blueprint is created to avoid circular import issues
from app.admin import routes