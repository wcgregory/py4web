"""
This file defines the database models
"""

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
    Field('first_name', length=40, required=True, notnull=False),
    Field('surname', length=40, required=True, notnull=False),
    Field('first_name', length=40, required=True, notnull=False),
    Field('age', length=3, type='integer', notnull=False),
)
db.define_table(
    'item',
    Field('name', length=60, required=True, notnull=False),
    Field('owner_id', db.person)
)
db.commit()
