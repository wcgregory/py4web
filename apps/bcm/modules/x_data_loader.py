# coding: utf-8 #

import logging

# from .bcm_db import BCMDb
from ..models import db
from .devices import DBDevices
from .commands import DBCommands


DEVICES = [
    {
        "name": "rtra-dumy-0001",
        "mgmt_ip": "123.123.123.1",
        "vendor": "Arista",
        "device_function": "Router",
        "device_roles": "CORE",
        "commands": [],
        "region": "EMEA",
        "site_code": "HACL"
    },
    {
        "name": "rtra-dumy-0002",
        "mgmt_ip": "123.123.123.2",
        "vendor": "Arista",
        "device_function": "Router",
        "device_roles": "CORE",
        "commands": [],
        "region": "EMEA",
        "site_code": "HACL"
    }
]

COMMANDS = [
    {
        "syntax": "show version",
        "vendors": ['Arista', 'Cisco', 'Juniper'],
        "device_functions": ['Firewall', 'Switch', 'Router'],
        "device_roles": ['CORE'],
    }
]

for device in DEVICES:
    record = DBDevices()
    record.from_json(device)
    if not record.db_loaded or not record.db_create:
        record.set_db_record()

for command in COMMANDS:
    record = DBCommands()
    record.from_json(command)
    if not record.db_loaded or not record.db_create:
        record.set_db_record()

"""
db.define_table(
    'commands',
    Field('syntax', 'string', notnull=True),
    Field('vendors', 'list:string', requires=IS_IN_SET(VENDORS), notnull=True),
    Field('device_functions', 'list:string', requires=IS_IN_SET(DEVICE_FUNCTIONS), notnull=True),
    Field('device_roles', 'list:string', requires=IS_IN_SET(DEVICE_ROLES)),
    Field('created_at', 'datetime', update=datetime.now()),
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
    Field('created_at', 'datetime', update=datetime.now()),
    format='%(name)s %(mgmt_ip)s'
)

db.define_table(
    'results',
    Field('device', 'reference devices', notnull=True),
    Field('command', 'reference commands', notnull=True),
    Field('completed_at', 'datetime', notnull=True),
    Field('status', 'string', requires=IS_IN_SET(COMMAND_STATUSES), notnull=True),
    Field('last_run_at', 'datetime'),
    Field('Last_status', 'string', requires=IS_IN_SET(COMMAND_STATUSES)),
    Field('result', 'text'),
    Field('last_result', 'text'),
)

db.commit()
"""
