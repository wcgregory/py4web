# coding: utf-8 #

import logging

from pydal.objects import Row

from .bcm_db import BCMDb
from ..models import db


class DBCommand(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'commands'
    """
    def __init__(self, db_id=None, syntax=None, comment=None):
        """
        Standard constructor class
        """
        super(DBCommand, self).__init__(db_id=db_id)
        #self._dbtable = 'commands' -> db.tables == 'commands'
        self.syntax = syntax
        self.vendors = list()
        self.device_functions = list()
        self.device_roles = list()
        self.comment = comment
        self.created_at = None
        self.modified_on = None
        if self.db_id:
            self.load_by_id()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a command object from the DB table using the DB id
        ---
        :param db_rec: a valid command DB record
        :type db_rec: Row (pydal.objects.Row)
        :param db_id: a valid command DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.commands.id == rec_id).select().first()    
        if not db_rec:
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        self.db_id = db_rec.id
        self.syntax = db_rec.syntax
        self.vendors = db_rec.vendors
        self.device_functions = db_rec.device_functions
        self.device_roles = db_rec.device_roles
        self.comment = db_rec.comment
        self.created_at = db_rec.created_at
        self.modified_on = db_rec.modified_on
        self.db_loaded = True
    
    def save(self):
        """
        Save a record to DB - creator/updater method
        Must set the class db_id to the new DB id
        ---
        :return True or False: based on whether a new record is created or not
        """
        query = (db.commands.syntax == self.syntax)
        if db(query).count() == 0:  # no existing db record matching 'syntax'
            self.created_at = DBCommand.get_timestamp()
            self.modified_on = self.created_at
            db.commands.insert(syntax=self.syntax, vendors=self.vendors,
                device_functions=self.device_functions, device_roles=self.device_roles,
                comment=self.comment, created_at=self.created_at, modified_on=self.modified_on)
            db.commit()
            db_rec = db(query).select().first()
            if db_rec:
                self.db_id = db_rec.id
                self.db_created = True
                logging.warning(f"New record created in table 'commands' id={self.db_id}")
                return True
        if db(query).count() > 0:  # no existing db record matching 'syntax'
            db_rec = db(query).select().first()
            self.db_id = db_rec.id
            vendor_updates = self.update_vendors(db_rec=db_rec)
            function_updates = self.update_functions(db_rec=db_rec)
            role_updates = self.update_roles(db_rec=db_rec)
            if not vendor_updates and not function_updates and not role_updates:
                logging.warning(f"No changes to save for id={self.db_id}")
                return False
            if vendor_updates:
                self.vendors = vendor_updates
            if function_updates:
                self.device_functions = function_updates
            if role_updates:
                self.device_roles = role_updates
            self.modified_on = DBCommand.get_timestamp()
            db.commands.update_or_insert(query,
                syntax=self.syntax, vendors=self.vendors, device_functions=self.device_functions,
                device_roles=self.device_roles, comment=self.comment, modified_on=self.modified_on)
            db.commit()
            logging.warning(f"Updated record in table 'commands' with id={self.db_id}")
            return True
        # catch-all error
        logging.warning("Unknown Error, more information/debugging required")
        db.rollback()
        return False
    
    def update_vendors(self, db_rec=None, db_id=None):
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id(default=db_id)
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.commands.id == rec_id).select().first()    
        if not db_rec or (db_rec and not isinstance(db_rec, Row)):
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        modified = False
        update_to_vendors = db_rec.vendors
        if self.vendors and isinstance(self.vendors, list):
            updates = [v.strip().capitalize() for v in self.vendors if not
                        v.strip().capitalize() in db_rec.vendors]
            if updates:
                update_to_vendors.extend(updates)
                modified = True
        if not modified:
            return None
        return sorted(update_to_vendors)
    
    def update_functions(self, db_rec=None, db_id=None):
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id(default=db_id)
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.commands.id == rec_id).select().first()    
        if not db_rec or (db_rec and not isinstance(db_rec, Row)):
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        modified = False
        update_to_functions = db_rec.device_functions
        if self.device_functions and isinstance(self.device_functions, list):
            updates = [df.strip().capitalize() for df in self.device_functions if not
                        df.strip().capitalize() in db_rec.device_functions]
            if updates:
                update_to_functions.extend(updates)
                modified = True
        if not modified:
            return None
        return sorted(update_to_functions)
    
    def update_roles(self, db_rec=None, db_id=None):
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id(default=db_id)
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.commands.id == rec_id).select().first()    
        if not db_rec or (db_rec and not isinstance(db_rec, Row)):
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        modified = False
        update_to_roles = db_rec.device_roles
        if self.device_roles and isinstance(self.device_roles, list):
            updates = [dr.strip().upper() for dr in self.device_roles if not
                        dr.strip().upper() in db_rec.device_roles]
            if updates:
                update_to_roles.extend(updates)
                modified = True
        if not modified:
            return None
        return sorted(update_to_roles)
    
    def delete(self, db_rec=None, db_id=None):
        """
        Delete DB record - destructor method
        If successful switch value of self.db_created and self.db_loaded to False
        ---
        :return True or False: based on whether record is deleted or not
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id(default=db_id)
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.commands.id == rec_id).select().first()
        if not db_rec or (db_rec and not isinstance(db_rec, Row)):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting Row received {type(db_rec)}")
        if db(db.devices.commands.contains(db_rec.id)).count() > 0:
            logging.warning(f"Unable to delete command id={db_rec.id} while used by device in 'devices'")
        elif db(db.results.command.belongs(db(db.commands.id == db_rec.id).select())).count() > 0:
            logging.warning(f"Unable to delete command id={db_rec.id} while in table 'results'")
        elif (
            db(db.devices.commands.contains(db_rec.id)).count() == 0 and
            db(db.results.command.belongs(db(db.commands.id == db_rec.id).select())).count() == 0
        ):
            db(db.devices.id == db_rec.id).delete()
            db.commit()
            logging.warning(f"Record id={db_rec.id} deleted from table 'commands'")
            self.db_id = None
            self.db_loaded = False
            self.db_created = False
            return True
        else:
            # catch all error
            logging.warning("Unknown error, more information/debugging required")
        return False

    def from_json(self, json_data):
        """
        Method to load a command object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'syntax' in json_data.keys() and json_data['syntax']:
            self.syntax = json_data['syntax'].strip()
        if 'vendors' in json_data.keys() and json_data['vendors']:
            self.vendors = [v.strip().capitalize() for v in json_data['vendors']]
        if 'device_functions' in json_data.keys() and json_data['device_functions']:
            self.device_functions = [df.strip().capitalize() for df in json_data['device_functions']]
        if 'device_roles' in json_data.keys() and json_data['device_roles']:
            self.device_roles = [role.strip().upper() for role in json_data['device_roles']]
        if 'comment' in json_data.keys() and json_data['comment']:
            self.comment =  json_data['comment'].strip()
        if 'created_at' in json_data.keys() and json_data['created_at']:
            self.created_at =  json_data['created_at']
        if 'modified_on' in json_data.keys() and json_data['modified_on']:
            self.modified_on = json_data['modified_on']
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, syntax=self.syntax, vendors=self.vendors,
            device_functions=self.device_functions, device_roles=self.device_roles,
            comment=self.comment, created_at=self.created_at, modified_on=self.modified_on)
