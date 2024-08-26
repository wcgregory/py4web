# coding: utf-8 #

import logging

from .bcm_db import BCMDb
from ..models import db


class DBCommands(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'commands'
    """
    def __init__(self, db_id=None, syntax=None):
        """
        Standard constructor class
        """
        super(DBCommands, self).__init__(db_id=db_id)
        #self._dbtable = 'commands' -> db.tables == 'commands'
        self.syntax = syntax
        self.vendors = list()
        self.device_functions = list()
        self.device_roles = list()
        self.created_at = None
        if self.db_id:
            self.load_by_id()
    
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
            db_rec = db(db.commands.id == rec_id).select().first()
        if not db_rec:
            logging.error("Unable to retrieve record, database record missing or invalid id")
        self.db_id = db_rec.id
        self.syntax = db_rec.syntax
        self.vendors = db_rec.vendors
        self.device_functions = db_rec.device_functions
        self.device_roles = db_rec.device_roles
        self.created_at = db_rec.created_at
        self.db_loaded = True
    
    def set_db_record(self):
        """
        Class to DB record creator
        Must set the class db_id to the new DB id
        """
        if self.db_id:
            raise ValueError("Device already has database id or record")
        # create query to check for linked fields
        query = db.commands.syntax == self.syntax
        query &= db.commands.vendors == self.vendors
        query &= db.commands.device_functions == self.device_functions
        if self.device_roles:
            query &= db.commands.device_roles.contains(self.device_roles, all=True)
        db_dup_check = db(query).select()
        if len(db_dup_check) > 0:
            rec_id = db_dup_check.first()
            logging.warning(f"Record already exists in table 'commands' with id:{rec_id.id}")
            return None
        db.commands.update_or_insert(query,
            syntax=self.syntax, vendors=self.vendors,
            device_functions=self.device_functions, device_roles=self.device_roles,
        )
        db_rec = db(query).select().first()
        if db_rec:
            self.db_id = db_rec.id
            self.db_create = True
            db.commit()
            logging.warning(f"Record created in table 'commands' with id:{self.db_id}")
        else:
            db.rollback()
    
    def from_json(self, json_data):
        """
        Method to load a device object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'syntax' in json_data.keys():
            self.syntax = json_data['syntax']
        if 'vendors' in json_data.keys():
            self.vendors = json_data['vendors']
        if 'device_functions' in json_data.keys():
            self.device_functions = json_data['device_functions']
        if 'device_roles' in json_data.keys():
            self.device_roles = json_data['device_roles']
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, syntax=self.syntax, vendors=self.vendors,
            device_functions=self.device_functions, device_roles=self.device_roles,
            created_at=self.created_at)
