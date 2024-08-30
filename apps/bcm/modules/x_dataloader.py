# coding: utf-8 #

import logging
from datetime import datetime

from ..models import db
from .devices import DBDevice
from .commands import DBCommand
from .results import DBResult


DEVICES = [
    {
        "name": "rtra-dumy-0001",
        "mgmt_ip": "123.123.123.1",
        "vendor": "Arista",
        "device_function": "Router",
        "device_roles": ["CORE"],
        "commands": [],
        "region": "EMEA",
        "site_code": "HACL"
    },
    {
        "name": "rtra-dumy-0002",
        "mgmt_ip": "123.123.123.2",
        "vendor": "Arista",
        "device_function": "Router",
        "device_roles": ['CORE'],
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
        "device_roles": ['CORE', 'GWAN']
    }
]

RESULTS = [
    {
        "device": 1,
        "command": 1,
        "completed_at": DBResult.get_timestamp(),
        "status": "Success",
        "result": "Sample data, for example, eos 4.30.5M",
    }
]

for device in DEVICES:
    record = DBDevice()
    record.from_json(device)
    record.save()

for command in COMMANDS:
    record = DBCommand()
    record.from_json(command)
    record.save()

#for result in RESULTS:
#    record = DBResult()
#    record.from_json(result)
#    record.save()
