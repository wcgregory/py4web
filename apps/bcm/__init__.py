from datetime import datetime
from py4web import action

from .models import db

@action('index')
def index():
    return f"Hello World @ {datetime.now()}"