"""HOD (Head of Department) Blueprint."""
from flask import Blueprint

bp = Blueprint('hod', __name__, url_prefix='/hod')

from app.hod import routes
