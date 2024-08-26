# coding: utf-8 #

import logging

from .bcm_db import BCMDb
from ..models import db


class DBDevices(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'devices'
    """
    def __init__(self, db_id=None, name=None, mgmt_ip=None):
        """
        Standard constructor class
        """
        super(DBDevices, self).__init__(db_id=db_id)
        self.name = name
        self.mgmt_ip = mgmt_ip
        self.vendor = None
        self.device_function = None
        self.device_roles = list()
        self.commands = list()
        self.region = None
        self.site_code = None
        self.created_at = None
        if self.db_id:
            self.load_by_id()
        #self._dbtable = 'devices'
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a device object from the DB table using the DB id
        ---
        :param db_rec: a valid device DB record
        :type db_rec: pydal.objects.Row
        :param db_id: a valid device DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                logging.error("Invalid or missing record id")
            db_rec = db(db.devices.id == rec_id).select().first()
        if not db_rec:
            logging.error("Unable to retrieve record, database record missing or invalid id")
        self.db_id = db_rec.id
        self.name = db_rec.name
        self.mgmt_ip = db_rec.mgmt_ip
        self.vendor = db_rec.vendor
        self.device_function = db_rec.device_function
        self.device_roles = db_rec.device_roles
        self.commands = db_rec.commands
        self.region = db_rec.region
        self.site_code = db_rec.site_code
        self.created_at = db_rec.created_at
        self.db_loaded = True
    
    def set_db_record(self):
        """
        Class to DB record creator
        Must set the class db_id to the new DB id
        """
        if self.db_id:
            raise ValueError("Device already has database id or record")
        # create query to check for duplicates of unique fields
        query = db.devices.name == self.name
        query |= db.devices.mgmt_ip == self.mgmt_ip
        db_dup_check = db(query).select()
        if len(db_dup_check) > 0:
            rec_id = db_dup_check.first()
            logging.warning(f"Duplicate entry in table 'devices' with id:{rec_id.id}")
            return None
        db.devices.update_or_insert(query,
            name=self.name, mgmt_ip=self.mgmt_ip, vendor=self.vendor,
            device_function=self.device_function, device_roles=self.device_roles,
            commands=self.commands, region=self.region, site_code=self.site_code
        )
        db_rec = db(query).select().first()
        if db_rec:
            self.db_id = db_rec.id
            self.db_create = True
            db.commit()
            logging.warning(f"Record created in table 'devices' with id:{self.db_id}")
        else:
            db.rollback()
    
    def from_json(self, json_data):
        """
        Method to load a device object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'name' in json_data.keys():
            self.name = json_data['name']
        if 'mgmt_ip' in json_data.keys():
            self.mgmt_ip = json_data['mgmt_ip']
        if 'vendor' in json_data.keys():
            self.vendor = json_data['vendor'].capitalize()
        if 'device_function' in json_data.keys():
            self.device_function = json_data['device_function'].capitalize()
        if 'device_roles' in json_data.keys():
            self.device_roles = json_data['device_roles'].upper()
        if 'commands' in json_data.keys():
            self.commands = json_data['commands']
        if 'region' in json_data.keys():
            self.region = json_data['region'].upper()
        if 'site_code' in json_data.keys():
            self.site_code = json_data['site_code'].upper()
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, name=self.name, mgmt_ip=self.mgmt_ip, vendor=self.vendor,
            device_function=self.device_function, device_roles=self.device_roles,
            commands=self.commands, region=self.region, site_code=self.site_code,
            created_at=self.created_at)


