"""
This file defines the database models
"""

from datetime import datetime

from .common import db, Field
from pydal.validators import *

VENDORS = ('Arista', 'Cisco', 'Juniper')
DEVICE_FUNCTIONS = ('Firewall', 'Router', 'Switch')
DEVICE_ROLES = ('CORE', 'GWAN', 'INTERNET', 'EXTRANET', 'OTHER')

REGIONS = ('APAC', 'SWIS', 'EMEA', 'AMER')
SITE_CODES = ('HACL', 'LO2X', 'LD2B', 'LODT')

COMMAND_STATUSES = ('Success', 'Pending', 'Running', 'Failed')

# Set development to True to repopulate DB
DEVELOPMENT = True

"""
if DEVELOPMENT:
    if 'commands' in db.tables:
        db.commands.truncate()
        db.commands.drop()
    if 'devices' in db.tables:
        db.devices.truncate()
        db.devices.drop()
    if 'results' in db.tables:
        db.results.truncate()
        db.results.drop()
"""

db.define_table(
    'commands',
    Field('syntax', 'string', notnull=True),
    Field('vendors', 'list:string', requires=IS_IN_SET(VENDORS), notnull=True),
    Field('device_functions', 'list:string', requires=IS_IN_SET(DEVICE_FUNCTIONS), notnull=True),
    Field('device_roles', 'list:string', requires=IS_IN_SET(DEVICE_ROLES)),
    Field('created_at', 'datetime', notnull=True),
    Field('modified_on', 'datetime'),
    format='%(syntax)s'
)

db.define_table(
    'devices',
    Field('name', 'string', length=24, notnull=True, unique=True),
    Field('mgmt_ip', 'string', length=15, unique=True),
    Field('vendor', 'string', requires=IS_IN_SET(VENDORS), notnull=True),
    Field('device_function', 'string', requires=IS_IN_SET(DEVICE_FUNCTIONS), notnull=True),
    Field('device_roles', 'list:string', requires=IS_IN_SET(DEVICE_ROLES), notnull=True),
    Field('commands', 'list:reference commands'),
    Field('region', 'string', requires=IS_IN_SET(REGIONS), notnull=True),
    Field('site_code', 'string', requires=IS_IN_SET(SITE_CODES), notnull=True),
    Field('comment', 'string'),
    Field('created_at', 'datetime', notnull=True),
    Field('modified_on', 'datetime'),
    format='%(name)s %(mgmt_ip)s'
)

db.define_table(
    'results',
    Field('device', 'reference devices', notnull=True),
    Field('command', 'reference commands', notnull=True),
    Field('completed_at', 'datetime', notnull=True),
    Field('status', 'string', requires=IS_IN_SET(COMMAND_STATUSES), notnull=True),
    Field('result', 'text'),
    Field('last_result', 'reference results')
    #Field('last_result', 'reference results', requires=IS_IN_DB(db, results.id))
    #Field('last_run_at', 'datetime'),
    #Field('last_status', 'string', requires=IS_IN_SET(COMMAND_STATUSES)),
    #Field('last_result', 'text'),
)

db.commit()
