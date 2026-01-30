from flask import Blueprint

bp = Blueprint('main', __name__)

# Import routes at the bottom (after blueprint creation)
from app.main import routes