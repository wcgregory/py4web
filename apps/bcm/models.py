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

if DEVELOPMENT:
    if 'commands' in db.tables:
        db.commands.drop()
    if 'devices' in db.tables:
        db.devices.drop()
    if 'results' in db.tables:
        db.results.drop()

db.define_table(
    'commands',
    Field('syntax', 'string', notnull=True),
    Field('vendors', 'list:string', requires=IS_IN_SET(VENDORS), notnull=True),
    Field('device_functions', 'list:string', requires=IS_IN_SET(DEVICE_FUNCTIONS), notnull=True),
    Field('device_roles', 'list:string', requires=IS_IN_SET(DEVICE_ROLES)),
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
    Field('site', 'string', requires=IS_IN_SET(SITE_CODES), notnull=True),
    format='%(name)s %(mgmt_ip)s'
)

db.define_table(
    'results',
    Field('device', 'reference devices'),
    Field('command', 'reference commands'),
    Field('completed_at', 'datetime'),
    Field('status', 'string', requires=IS_IN_SET(COMMAND_STATUSES), notnull=True),
    Field('last_run_at', 'datetime'),
    Field('Last_status', 'string', requires=IS_IN_SET(COMMAND_STATUSES)),
    Field('result', 'text'),
    Field('last_result', 'text'),
)

db.commit()
