"""
This file defines the database models
"""

from datetime import datetime

from .common import db, Field
from pydal.validators import *

VENDORS = ('Arista', 'Cisco', 'Juniper')
DEVICE_OS = ('eos', 'veos', 'ios', 'nxos', 'iosxr', 'junos')
DEVICE_FUNCTIONS = ('Firewall', 'Router', 'Switch')
DEVICE_ROLES = ('CORE', 'GWAN', 'INTERNET', 'EXTRANET', 'OTHER')

REGIONS = ('APAC', 'SWIS', 'EMEA', 'AMER')
SITE_CODES = ('HACL', 'LO2X', 'LD2B', 'LODT')

COMMAND_STATUSES = ('Success', 'Pending', 'Running', 'Failed', 'Completed')

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
    Field('comment', 'string'),
    Field('output_parsers', 'list:reference output_parsers'),
    Field('created_at', 'datetime', notnull=True),
    Field('modified_on', 'datetime'),
    format='%(syntax)s'
)

db.define_table(
    'output_parsers',
    Field('vendor', 'string', requires=IS_IN_SET(VENDORS), notnull=True),
    Field('command', 'reference commands', notnull=True),
    Field('device_os', 'string', notnull=True),
    Field('is_json', 'boolean'),
    Field('parser_path', 'list:string', notnull=True),
    Field('main_keys', 'list:string'),
    Field('ignore_keys', 'list:string'),
    Field('name', 'string'),
    Field('created_at', 'datetime', notnull=True),
    Field('modified_on', 'datetime'),
    format='%(vendor)s %(device_os)s %(name)s'
)

db.define_table(
    'devices',
    Field('name', 'string', length=24, notnull=True, unique=True),
    Field('mgmt_ip', 'string', length=15, unique=True),
    Field('vendor', 'string', requires=IS_IN_SET(VENDORS), notnull=True),
    Field('os', 'string', requires=IS_IN_SET(DEVICE_OS), notnull=True),
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
    'jobs',
    Field('name', 'string', length=128, notnull=True, unique=True),
    Field('devices', 'list:reference devices'),
    Field('results', 'list:reference results'),
    Field('started_at', 'datetime'),
    Field('completed_at', 'datetime'),
    Field('status', 'string', requires=IS_IN_SET(COMMAND_STATUSES)),
    Field('comment', 'string'),
    format='%(name)s %(comment)s'
)

db.define_table(
    'results',
    Field('device', 'reference devices', notnull=True),
    Field('command', 'reference commands', notnull=True),
    Field('completed_at', 'datetime', notnull=True),
    Field('status', 'string', requires=IS_IN_SET(COMMAND_STATUSES), notnull=True),
    Field('job', 'reference jobs', notnull=True),
    Field('result', 'text'),
    Field('last_result', 'reference results'),
    Field('comment', 'string'),
    format='%(comment)s'
)

db.commit()
