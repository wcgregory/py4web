import datetime
from py4web import action

from .models import db, list_people, list_items, ownership, owned_by_user

@action('index')
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

@action('people')
def people():
    person_list = list_people()
    return person_list

@action('items')
def items():
    item_list = list_items()
    return item_list

@action('owners')
def owners():
    owners = ownership()
    return owners

@action('people/<id>')
def people(id):
    userItems = owned_by_user(id)
    return userItems.keys()

@action('people/<id>/items')
def people(id):
    userItems = owned_by_user(id)
    return list(userItems.values())[0]
