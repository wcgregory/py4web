# coding: utf-8

import logging
import json

from pydal.objects import Row

from ..models import db
from ..modules.devices import DBDevice
from ..modules.commands import DBCommand
from ..modules.results import DBResult
#from ..modules.output_parsers import DBParser


"""      
>>> from apps.bcm.controllers.device_manager import DeviceManager
>>> dm = DeviceManager()
>>> dm.load(4)
>>> dm.num_commands
2
>>> dm.num_results
11
>>> dm.to_json()
"""


class DeviceManager():
    """
    Mediator class to control 'device' object interactions
    """
    def __init__(self, device=None):
        """
        Standard constructor class
        """
        self.device = device
        self.commands = None
        self.num_commands = None
        self.results = None
        self.num_results = None
    
    @classmethod
    def get_devices(cls, device=None):
        if not device:
            devices = db(db.devices).select()
        else:
            if isinstance(device, int):
                devices = db(db.devices.id == device).select()
            if isinstance(device, str):
                devices = db((db.devices.mgmt_ip == device) | (db.devices.name == device)).select().first()
        device_list = list()
        for dev in devices:
            dm = DeviceManager()
            dm.load(dev.id)
            device_list.append(dm.to_json())
        return device_list
    
    def load(self, device):
        """Create 'device' object and load the related objects"""
        if isinstance(device, int):
            d = DBDevice(db_id=device)
        elif isinstance(device, Row):
            d = DBDevice()
            d.load_by_id(db_rec=device)
        if not d:
            logging.warning(f"Expected 'device' object, received {type(d)}")
            return None
        self.device = d
        self.commands = [DBCommand(db_id=cmd) for cmd in self.device.commands]
        self.results = self.get_results()
        self.num_commands = self.commands_count
        self.num_results = self.results_count
    
    @property
    def commands_count(self):
        return len(self.commands)
    
    @property
    def results_count(self):
        return len(self.results)
    
    def get_results(self):
        """Return a list of 'result' objects loaded from the DB table 'results'"""
        results_by_device = db(db.results.device == self.device.db_id).select()
        results = [DBResult(db_id=result.id) for result in results_by_device]
        return results
    
    def commands_to_json(self):
        """
        Returns a list of commands in dict format
        ---
        :return commands: list containing a subset of the 'commands' object (key=DB id value=syntax)
        :rtype commands: list
        """
        commands = {cmd.db_id: cmd.syntax for cmd in self.commands}
        return commands
    
    def results_to_json(self):
        """
        Returns a list of results in dict format
        ---
        :return results: list conatining the full dataset of results in dict format
        :rtype results: list
        """
        results = {result.db_id: result.to_json() for result in self.results}
        return results
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        device = self.device.to_json()
        commands = self.commands_to_json()
        results = self.results_to_json()
        device.update({'commands': commands})  #overwrite 'commands' entry
        device.update({'results': results})
        return device
