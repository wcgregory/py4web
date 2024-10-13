# coding: utf-8 #

from datetime import datetime

from .devices import DBDevice
from .commands import DBCommand
from .results import DBResult
from .jobs import DBJob
from .network_poller import NetworkPoller
from .output_parsers import DBParser

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
        "name": "rtrj-dumy-6001",
        "mgmt_ip": "123.123.123.61",
        "vendor": "Juniper",
        "os": "junos",
        "device_function": "Router",
        "device_roles": ['INTERNET'],
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
        "device_roles": ['CORE', 'GWAN'],
    }
]

JOBS = [
    {
        "name": "job_1",
        "devices": [1],
        "results": [1],
        "started_at":"2024-09-01 10:28:10",
        "completed_at": "2024-09-01 10:28:14",
        "status": "Success",
    },
    {
        "name": "job_2",
        "devices": [1, 2],
        "results": [2, 3],
        "started_at":"2024-09-01 14:28:32",
        "completed_at": "2024-09-01 14:30:58",
        "status": "Success",
    },
    {
        "name": "job_3",
        "devices": [4],
        "results": [4],
        "started_at":"2024-09-07 19:55:30",
        "completed_at": "2024-09-07 19:55:39",
        "status": "Success",
    },
]

RESULTS = [
    {
        "device": 1,
        "command": 1,
        "completed_at": "2024-09-01 10:28:14",
        "status": "Success",
        "job": 1,
        "result": "Sample data, for example, eos 4.30.5M",
    },
    {
        "device": 1,
        "command": 1,
        "completed_at": "2024-09-01 14:28:32",
        "status": "Success",
        "job": 2,
        "result": "Sample data, for example, eos 4.30.5M",
    },
    {
        "device": 2,
        "command": 1,
        #"completed_at": DBResult.get_timestamp(),
        "completed_at": "2024-09-01 14:30:58",
        "status": "Success",
        "job": 2,
        "result": "Sample data, for example, eos 4.30.5M",
    },
    {
        "device": 4,
        "command": 2,
        "completed_at": "2024-09-07 19:55:39",
        "status": "Success",
        "job": 3,
        "result": "{'TABLE_intf': {'ROW_intf': [{'vrf-name-out': 'default', 'intf-name': 'Vlan10', 'proto-state': 'down', 'link-state': 'down', 'admin-state': 'down', 'iod': '77', 'prefix': '192.168.1.1', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Vlan20', 'proto-state': 'down', 'link-state': 'down', 'admin-state': 'up', 'iod': '78', 'prefix': '192.168.2.1', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Vlan30', 'proto-state': 'down', 'link-state': 'down', 'admin-state': 'up', 'iod': '79', 'prefix': '192.168.3.1', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Vlan59', 'proto-state': 'down', 'link-state': 'down', 'admin-state': 'down', 'iod': '85', 'prefix': '192.168.59.1', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Lo1', 'proto-state': 'up', 'link-state': 'up', 'admin-state': 'up', 'iod': '73', 'prefix': '192.168.1.2', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Lo20', 'proto-state': 'down', 'link-state': 'down', 'admin-state': 'down', 'iod': '70', 'prefix': '10.20.30.1', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Lo59', 'proto-state': 'up', 'link-state': 'up', 'admin-state': 'up', 'iod': '84', 'prefix': '59.59.59.59', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Lo77', 'proto-state': 'up', 'link-state': 'up', 'admin-state': 'up', 'iod': '75', 'prefix': '10.77.77.1', 'ip-disabled': 'FALSE'}, {'vrf-name-out': 'default', 'intf-name': 'Eth1/59', 'proto-state': 'down', 'link-state': 'down', 'admin-state': 'down', 'iod': '63', 'prefix': '192.168.59.254', 'ip-disabled': 'FALSE'}]}}",
        "comment": "Success @2024-09-07 19:55:39"
    }
]

PARSERS = [    
    {
        "vendor": "Cisco",
        "command": 1,
        "device_os": "nxos",
        "is_json": True,
        "parser_path": [],
        "name": "nxos_sho_version"
    },
    {
        "vendor": "Cisco",
        "command": 2,
        "device_os": "nxos",
        "is_json": True,
        "parser_path": ["TABLE_intf", "ROW_intf"],
        "name": "nxos_sho_ip_int_brief"
    },
    {
        "vendor": "Cisco",
        "command": 1,
        "device_os": "ios",
        "is_json": True,
        "parser_path": [],
        "name": "ios_sho_version"
    },
    {
        "vendor": "Cisco",
        "command": 2,
        "device_os": "ios",
        "is_json": True,
        "parser_path": [],
        "name": "ios_sho_ip_int_brief"
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

for job in JOBS:
    record = DBJob()
    record.from_json(job)
    record.save()

for result in RESULTS:
    record = DBResult()
    record.from_json(result)
    record.save()

for parser in PARSERS:
    record = DBParser()
    record.from_json(parser)
    record.save()

"""
device = NetworkPoller(device_id=3)
device.load_device_commands()
device.run_device_commands(auth=('admin', 'C1sco12345'))
device.save_results()

device = NetworkPoller(device_id=4)
device.load_device_commands()
device.run_device_commands(auth=('admin', 'Admin_1234!'))
device.save_results()

    def run(self, credentials=None):
        #credentials
        for device in self.devices:
            j = NetworkPoller(device_id=device, job_id=self.db_id)
            j.load_device_commands()
            j.run_device_commands(auth=credentials)
            j.save_results()

job = DBJob("job_test")
job.set_devices()
"""

add_cmdparser = DBCommand(1)
add_cmdparser.update_output_parsers()

add_cmdparser = DBCommand(2)
add_cmdparser.update_output_parsers()
