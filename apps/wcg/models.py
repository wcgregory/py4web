"""
This file defines the database models
"""
from datetime import datetime
from .common import db, Field
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

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
    Field('name', length=60, required=True, notnull=False),
    Field('owner_id', db.person)
)

db.commit()
