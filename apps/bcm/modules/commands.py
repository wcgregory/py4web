# coding: utf-8 #

import logging

from pydal.objects import Row
from .bcm_db import BCMDb
from ..models import db


class DBCommand(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'commands'
    """
    def __init__(self, db_id=None, syntax=None):
        """
        Standard constructor class
        """
        super(DBCommand, self).__init__(db_id=db_id)
        #self._dbtable = 'commands' -> db.tables == 'commands'
        self.syntax = syntax
        self.vendors = list()
        self.device_functions = list()
        self.device_roles = list()
        self.created_at = None
        self.modified_on = None
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
                return False
            db_rec = db(db.commands.id == rec_id).select().first()
        if not db_rec:
            logging.error("Unable to retrieve record, database record missing or invalid id")
            return False
        self.db_id = db_rec.id
        self.syntax = db_rec.syntax
        self.vendors = db_rec.vendors
        self.device_functions = db_rec.device_functions
        self.device_roles = db_rec.device_roles
        self.created_at = db_rec.created_at
        self.modified_on = db_rec.modified_on
        self.db_loaded = True
    
    def save(self):
        """
        Class to DB record creator
        Must set the class db_id to the new DB id
        ---
        :return True or False: based on whether a new record is created or not
        """
        if self.db_id:
            raise ValueError("Command already has database id or record")
        # create query to check record's key fields, starting with 'syntax'
        query = (db.commands.syntax == self.syntax)
        if db(query).count() == 0:  # no existing db record matching 'syntax'
            self.created_at = DBCommand.get_timestamp()
            self.modified_on = self.created_at
            db.commands.insert(syntax=self.syntax, vendors=self.vendors,
                device_functions=self.device_functions, device_roles=self.device_roles,
                created_at=self.created_at, modified_on=self.modified_on)
            db.commit()
            db_rec = db(query).select().first()
            if db_rec:
                self.db_id = db_rec.id
                self.db_created = True
                logging.warning(f"New record created in table 'commands' id={self.db_id}")
            return True
        elif db(query).count() > 0:  # existing db record matching 'syntax'
            db_rec = db(query).select().first()
            self.db_id = db_rec.id
            vendor_updated = self.is_vendor_updated(db_id=self.db_id)
            # create specific query using DB id, with key field 'vendors'
            query = (db.commands.id == self.db_id)
            query &= (db.commands.vendors.contains(self.vendors, all=True))
        if db(query).count() == 0:
            vendor_updates = db_rec.vendors
            vendor_updates.extend([
                vu.strip().capitalize() for vu in self.vendors if not vu.strip().capitalize() in db_rec.vendors
            ])
            self.modified_on = DBCommand.get_timestamp()
            db_rec.update_record(vendors=sorted(vendor_updates), modified_on=self.modified_on)
            db.commit()
            logging.warning(f"Update record id={self.db_id} field='vendors' in table 'commands'")
            return True
        # add to query pair 'syntax'|'vendor' with key field 'device_functions'
        query &= (db.commands.device_functions.contains(self.device_functions, all=True))
        if db(query).count() == 0:
            function_updates = db_rec.device_functions
            function_updates.extend([
                fu.strip().upper() for fu in self.function_updates if not
                    fu.strip().upper() in db_rec.device_functions
            ])
            self.modified_on = DBCommand.get_timestamp()
            db_rec.update_record(device_functions=sorted(function_updates), modified_on=self.modified_on)
            db.commit()
            logging.warning(f"Update record id={self.db_id} field='device_functions' in table 'commands'")
            return True
        # restart with specific query using DB id, with key field 'vendors', adding 'device_roles'
        query = (db.commands.id == self.db_id) & (db.commands.vendors.contains(self.vendors, all=True))
        query &= (db.commands.device_roles.contains(self.device_roles, all=True))
        if db(query).count() == 0:
            role_updates = db_rec.device_roles
            role_updates.extend([
                ru.strip().upper() for ru in self.device_roles if not
                    ru.strip().upper() in db_rec.device_roles
            ])
            self.modified_on = DBCommand.get_timestamp()
            db_rec.update_record(device_roles=sorted(role_updates), modified_on=self.modified_on)
            db.commit()
            logging.warning(f"Update record id={self.db_id} field='device_roles' in table 'commands'")
            return True
        logging.warning(f"No updates to id={self.db_id} in table 'commands'")
        db.rollback()
        return False
    
    def is_vendor_updated(self, db_rec=None, db_id=None):
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                logging.error("Invalid or missing record id")
                return None
            db_rec = db(db.commands.id == rec_id).select().first()
            if not db_rec:
                logging.error("Unable to retrieve record, database record missing or invalid id")
                return None
        #elif db_rec and isinstance(db_rec, Row):
        #updated_vendors = list()
        #else:
        query = (db.commands.id == db_id) & (db.commands.vendors.contains(self.vendors, all=True))
        if db(query).count() == 0:
            return None
        db_rec = db(query).select().first()
        updated_vendors = db_rec.vendors
        update = [
            v.strip().capitalize() for v in self.vendors if not v.strip().capitalize() in db_rec.vendors
        ]
        if update:
            return sorted(updated_vendors.extend(update))
        return None
    
    def from_json(self, json_data):
        """
        Method to load a device object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'syntax' in json_data.keys() and json_data['syntax']:
            self.syntax = json_data['syntax'].strip()
        if 'vendors' in json_data.keys() and json_data['vendors']:
            self.vendors = [v.strip().capitalize() for v in json_data['vendors']]
        if 'device_functions' in json_data.keys() and json_data['device_functions']:
            self.device_functions = [df.strip().capitalize() for df in json_data['device_functions']]
        if 'device_roles' in json_data.keys() and json_data['device_roles']:
            self.device_roles = [entry.strip().upper() for entry in json_data['device_roles']]
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, syntax=self.syntax, vendors=self.vendors,
            device_functions=self.device_functions, device_roles=self.device_roles,
            created_at=self.created_at, modified_on=self.modified_on)
