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

MANUFACTURER = ('Arista', 'Cisco', 'Juniper')
DEVICE_TYPE = ('Firewall', 'Router', 'Switch')
DEVICE_ROLE = ('DC-CORE', 'GWAN', 'INTERNET', 'EXTRANET', 'OTHER')

REGION = ('APAC', 'SWIS', 'EMEA', 'AMER')
SITE = ('HACL', 'LO2X', 'LD2B', 'LODT')

if 'device' in db.tables:
    db.device.drop()
if 'device-role' in db.tables:
    db.device_role.drop()

db.define_table(
    'device',
    Field('name', length=24, required=True, notnull=True, unique=True),
    Field('mgmt_ip', length=15, unique=True),
    Field('make', required=True, requires=IS_IN_SET(MANUFACTURER)),
    Field('function', required=True, requires=IS_IN_SET(DEVICE_TYPE)),
    Field('region', required=True, requires=IS_IN_SET(REGION)),
    Field('site', required=True, requires=IS_IN_SET(SITE)),
    format='%(name)s'
)

db.define_table(
    'device_role',
    Field('device_id', 'reference device'),
    Field('role', required=True, requires=IS_IN_SET(DEVICE_ROLE)),
    format='%(role)s %(device_id)s'
)

db.define_table(
    'command',
    Field('syntax', required=True, notnull=True, unique=True),
    Field('make', required=True, requires=IS_IN_SET(MANUFACTURER)),
    format='%(syntax)s'
)

db.define_table(
    'compatible_command',
    Field('command_id', 'reference device'),
    Field('function', required=True, requires=IS_IN_SET(DEVICE_TYPE)),
    format='%(function)s'
)

db.define_table(
    'command_list',
    Field('name', length=96, required=True, notnull=True, unique=True),
    Field('command_id', 'reference device'),
    Field('role', required=True, requires=IS_IN_SET(DEVICE_ROLE)),
    format='%(name)s %(role)s'
)
