"""
This file defines the database models
"""
from datetime import datetime
from .common import db, Field
from pydal.validators import *
from .tasks.data_import import people, items

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

if 'person' in db.tables:
    db.person.drop()
if 'item' in db.tables:
    db.item.drop()
if 'owner' in db.tables:
    db.owner.drop()

db.define_table(
    'person',
    Field('first_name', length=40, required=True, notnull=True),
    Field('surname', length=40, required=True, notnull=True),
    Field('email', length=64, required=True, notnull=True, unique=True),
    Field('username', length=24, unique=True),
    Field('age', length=3, type='integer'),
)

db.define_table(
    'item',
    Field('name', length=60, required=True, notnull=False, unique=True),
)

db.define_table(
    'owner',
    Field('person_id', 'reference person'),
    Field('item_id', 'reference item')
)

for person in people:
    if "age" in person.keys():
        db.person.update_or_insert(db.person.username == person["username"],
            first_name=person["firstname"],
            surname=person["surname"],
            email=person["email"],
            username=person["username"],
            age=person["age"]
        )
    else:
        db.person.update_or_insert(db.person.username == person["username"],
            first_name=person["firstname"],
            surname=person["surname"],
            email=person["email"],
            username=person["username"],
        )

for item in items:
    db.item.update_or_insert(db.item.name == item,
        name=item
    )

for item in items:
    if item == 'cup':
        db.owner.update_or_insert(
            (db.owner.person_id == 1) & (db.owner.item_id == 4),
            person_id = 1,
            item_id = 4
        )
    elif item == 'glass':
        db.owner.update_or_insert(
            (db.owner.person_id == 2) & (db.owner.item_id == 5),
            person_id = 2,
            item_id = 5
        )
    else:
        indx = 1
        while indx <= 3:
            for person in db(db.person).select():
                db.owner.update_or_insert(
                    (db.owner.person_id == person.id) & (db.owner.item_id == indx),
                    person_id = person.id,
                    item_id = indx
                )
            indx += 1

db.commit()


class Person():
    def __init__(self):
        self.first_name = None  #str 
        self.surname = None  #str
        self.email = None  #str
        self.username = None  #str
        self.age = None  #int


def list_people():
    person_list = []
    for person in db(db.person).select():
        person_name = f"{person.first_name} {person.surname}"
        person_list.append(person_name)
    return person_list


def list_items():
    item_list = []
    for item in db(db.item).select():
        item_list.append(item.name)
    return item_list

def ownership():
    owned_by = []
    ownership = db(
        (db.person.id == db.owner.person_id) &
        (db.item.id == db.owner.item_id)
    )
    #ordered_owner = ownership.select(db.person.ALL, orderby=db.person.surname)
    #for owner in ordered_owner:
    for owner in ownership.select():
        owned_by.append(f"{owner.person.first_name} {owner.person.surname} owns "
                        f"{owner.item.name}")
    return sorted(owned_by)

def owned_by_user(id):
    person = db.person
    user_id = person.id
    query = user_id == id
    results = db(query).select()
    try:
        user = f"{results[0].first_name} {results[0].surname}"
    except:
        user = "Unknown"
        return {user: []}
    items = []
    for item in results[0].owner.select():
        #entry = db(db.item.id == item.item_id).select(db.item.name)
        #items.append(entry[0].name)
        items.append(db(db.item.id == item.item_id).select(db.item.name)[0].name)
    #for id in item_ids:
    #    item_names.append(db(db.item.id == id).select(item.name))
    return {user: items}
    

