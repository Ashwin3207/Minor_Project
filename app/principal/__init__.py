"""Principal Blueprint."""
from flask import Blueprint

bp = Blueprint('principal', __name__, url_prefix='/principal')

from app.principal import routes
