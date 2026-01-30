from flask import Blueprint

bp = Blueprint('student', __name__, url_prefix='/student')

# Import routes after blueprint definition to avoid circular imports
from app.student import routes