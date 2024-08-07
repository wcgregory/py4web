import datetime
from py4web import action


from .models import db

@action("index")
def index():
    return f"Hello World @ {datetime.datetime.now()}"

@action('colors')
def colors():
    return {'colors': ['red', 'blue', 'green']}

@action('color/<name>')
def color(name):
    if name in ['red', 'blue', 'green']:
        return 'You picked color %s' % name
    return 'Unknown color %s' % name
