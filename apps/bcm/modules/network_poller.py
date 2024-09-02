# coding: utf-8

import logging
from datetime import datetime

from ..models import db
from .bcm_db import BCMDb
from .devices import DBDevice
from .commands import DBCommand
from .results import DBResult
from .device_connector import NetConnect


class DBNetworkPoller():
    """
    DB Abstraction class for uniform interaction with DB Tables
    """
    def __init__(self, device_id=None):
        self.device = DBDevice(db_id=device_id)
        self.commands = None
        self.response = dict()
        self.results = None
    
    def run_device_commands(self, auth=None, commands=None):
        d = NetConnect(host=self.device.mgmt_ip, vendor=self.device.vendor)
        d.set_username(username=auth[0])
        d.set_password(password=auth[1])
        d.set_host_os(os=self.device.os)
        if not self.commands:
            self.load_device_commands()
        if not d.device_type:
            d.set_netmiko_device_type(vendor=self.device.vendor)
        d.connect_to_device()
        if not d.is_connected:
            return False
        else:
            for cmd_id in self.commands.keys():
                cmd_ref = f"{self.device.db_id}:{cmd_id}"
                self.response.update({cmd_ref: {
                    "device": self.device.db_id, "command": cmd_id
                }})
                if self.device.os == 'ios':
                    result = d.send_op_command(self.commands[cmd_id])
                else:
                    result = d.send_op_command_json(self.commands[cmd_id])
                result_time = self.device.get_timestamp()
                self.response[cmd_ref].update({"completed_at": result_time})
                if result:
                    result_status = 'Success'
                else:
                    result = 'Failure'
                    result_status = result
                self.response[cmd_ref].update({
                    "status": f"{result_status}",
                    "result": result,
                    "comment": f"{result_status} @{result_time}"
                })
    
    def load_device_commands(self, all=True, subset=None):
        """
        """
        self.commands = dict()
        if all:
            commands = [cmd_id for cmd_id in self.device.commands]
        elif subset and isinstance(subset, list):
            commands = [cmd_id for cmd_id in subset if cmd_id in self.device.commands]
        if not commands:
            raise ValueError(self.__class__.__name__, "No device commands available")
        for cmd_id in commands:
            c = DBCommand(db_id=cmd_id)
            self.commands.update({c.db_id: c.syntax})
            return True
        # catch all error
        logging.warning("Unknown error, more information/debugging required")
        return False
    
    def save_results(self):
        """
        """
        if self.response:
            for result in self.response.keys():
                r = DBResult()
                r.from_json(json_data=self.response[result])
                r.save()
