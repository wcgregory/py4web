# coding: utf-8 #

from datetime import datetime

from .devices import DBDevice
from .commands import DBCommand
from .results import DBResult
from .network_poller import DBNetworkPoller

DEVICES = [
    {
        "name": "rtra-dumy-0001",
        "mgmt_ip": "123.123.123.1",
        "vendor": "Arista",
        "os": "eos",
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
        "os": "eos",
        "device_function": "Router",
        "device_roles": ['CORE'],
        "commands": [],
        "region": "EMEA",
        "site_code": "HACL"
    },
    {
        "name": "cisco_ios-sandbox-01",
        "mgmt_ip": "sandbox-iosxe-latest-1.cisco.com",
        "vendor": "Cisco",
        "os": "ios",
        "device_function": "Router",
        "device_roles": ['CORE'],
        "commands": [1, 2],
        "region": "EMEA",
        "site_code": "HACL"
    },
    {
        "name": "cisco_nxos-sandbox-01",
        "mgmt_ip": "sbx-nxos-mgmt.cisco.com",
        "vendor": "Cisco",
        "os": "nxos",
        "device_function": "Router",
        "device_roles": ['CORE'],
        "commands": [1, 2],
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
    },
    {
        "syntax": "show ip interface brief",
        "vendors": ['Arista', 'Cisco'],
        "device_functions": ['Firewall', 'Switch', 'Router'],
        "device_roles": ['CORE', 'GWAN']
    }
]

RESULTS = [
    {
        "device": 1,
        "command": 1,
        "completed_at": '2024-09-01 14:28:32',
        "status": "Success",
        "result": "Sample data, for example, eos 4.30.5M",
    },
    {
        "device": 2,
        "command": 1,
        #"completed_at": DBResult.get_timestamp(),
        "completed_at": "2024-09-01 14:30:58",
        "status": "Success",
        "result": "Sample data, for example, eos 4.30.5M",
    },
    {
        "device": 1,
        "command": 1,
        "completed_at": '2024-09-01 10:28:14',
        "status": "Success",
        "result": "Sample data, for example, eos 4.30.5M",
    },
    {
        "device": 1,
        "command": 1,
        "completed_at": '2024-09-01 10:28:55',
        "status": "Success",
        "result": "Sample data, for example, eos 4.30.5M",
    },
    {
        "device": 1,
        "command": 1,
        "completed_at": '2024-09-01 10:28:14',
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

for result in RESULTS:
    record = DBResult()
    record.from_json(result)
    record.save()

device = DBNetworkPoller(device_id=3)
device.load_device_commands()
device.run_device_commands(auth=('admin', 'C1sco12345'))
device.save_results()

device = DBNetworkPoller(device_id=4)
device.load_device_commands()
device.run_device_commands(auth=('admin', 'Admin_1234!'))
device.save_results()
