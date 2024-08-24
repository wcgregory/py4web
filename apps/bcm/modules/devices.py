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
        super().__init__(db_id)
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
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a device object from the DB using the DB id
        ---
        :param db_rec: a valid device DB record
        :type db_rec: pyDAL object
        :param db_id:
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


