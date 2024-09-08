# coding: utf-8

import logging

from pydal.objects import Row

from ..models import db
from .bcm_db import BCMDb
#from .commands import DBCommand


class DBParser(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'command_parsers'
    """
    def __init__(self, db_id=None):
        """
        Standard constructor class
        """
        super(DBParser, self).__init__(db_id=db_id)
        #self._dbtable = 'command_parsers' -> db.tables == 'command_parsers'
        self.vendor = None
        self.command = None
        self.device_os = None
        self.is_json = bool()
        self.parser_path = list()  # path to main body of response output
        self.main_keys = list()
        self.name = None
        self.created_at = None
        self.modified_on = None
        if self.db_id:
            self.load_by_id()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a command_parser object from the DB table using the DB id
        ---
        :param db_rec: a valid command_parser DB record
        :type db_rec: Row (pydal.objects.Row)
        :param db_id: a valid command_parser DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.command_parsers.id == rec_id).select().first()    
        if not db_rec:
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        self.db_id = db_rec.id
        self.vendor = db_rec.vendor
        self.command = db_rec.command
        self.device_os = db_rec.device_os
        self.is_json = db_rec.is_json
        self.parser_path = db_rec.parser_path
        self.main_keys = db_rec.main_keys
        self.name = db_rec.name
        self.created_at = db_rec.created_at
        self.modified_on = db_rec.modified_on
        self.db_loaded = True
    
    def load_by_command(self, db_rec=None, db_id=None, command_id=None):
        """
        Method to load a command_parser object from the DB table using the command id
        Condition: will only load if device_os matches
        ---
        :param command_id: a valid command DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.command_parsers.id == rec_id).select().first()    
        if not db_rec:
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        
        self.db_id = db_rec.id
        self.vendor = db_rec.vendor
        self.command = db_rec.command
        self.device_os = db_rec.device_os
        self.is_json = db_rec.is_json
        self.parser_path = db_rec.parser_path
        self.main_keys = db_rec.main_keys
        self.name = db_rec.name
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
        # query to check whether record exists as 'vendor, 'command', 'os' & 'is_json'
        query = (db.command_parsers.vendor == self.vendor) & (
            db.command_parsers.command == self.command)
        query &= (db.command_parsers.device_os == self.device_os) & (
            db.command_parsers.is_json == self.is_json)
        if db(query).count() == 0:
            # create query to check for duplicates of unique fields before save
            is_unique = (db.command_parsers.name == self.name)
            if db(is_unique).count() > 0:
                logging.warning(f"Duplicate value in 'command_parsers' for name={self.name}")
                return False
            self.created_at = DBParser.get_timestamp()
            self.modified_on = self.created_at
            db.command_parsers.insert(vendor=self.vendor, command=self.command,
                device_os=self.device_os, is_json=self.is_json,
                parser_path=self.parser_path, main_keys=self.main_keys, name=self.name,
                created_at=self.created_at, modified_on=self.modified_on)
            db.commit()
            db_rec = db(query).select().first()
            if db_rec:
                self.db_id = db_rec.id
                self.db_created = True
                logging.warning(f"New record created in table 'command_parsers' id={self.db_id}")
                return True
        elif db(query).count() > 0:
            db_rec = db(query).select().first()
            self.db_id = db_rec.id
            if not self.is_record_modified(db_rec=db_rec):
                logging.warning(f"No changes to save for id={self.db_id}")
                return False
            self.modified_on = DBParser.get_timestamp()
            db.command_parsers.update_or_insert(query,
                vendor=self.vendor, command=self.command, device_os=self.device_os,
                is_json=self.is_json, parser_path=self.parser_path, main_keys=self.main_keys,
                name=self.name, modified_on=self.modified_on)
            db.commit()
            logging.warning(f"Updated record in table 'command_parsers' with id={self.db_id}")
            return True
        # catch-all error
        logging.warning("Unknown Error, more information/debugging required")
        db.rollback()
        return False
    
    def is_record_modified(self, db_rec=None, db_id=None):
        """
        Method to detect changes between class and DB record on unqueried fields
        ---
        :param db_rec: a valid command_parsers DB record
        :type db_rec: Row (pydal.objects.Row)
        :param db_id: a valid command_parsers DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.command_parsers.id == rec_id).select().first()
        elif db_rec and not isinstance(db_rec, Row):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting Row received {type(db_rec)}")
        if (
            self.parser_path != db_rec.parser_path or
            self.main_keys != db_rec.main_keys or
            self.name != db_rec.name
        ):
            return True
        # catch-all
        return False
    
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
            db_rec = db(db.command_parsers.id == rec_id).select().first()
        if not db_rec or (db_rec and not isinstance(db_rec, Row)):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting Row received {type(db_rec)}")
        if db(db.commands.parser_path.contains(db_rec.id)).count() > 0:
            logging.warning(f"Unable to delete 'command_parsers' id={db_rec.id} while used "
                            "as an 'parser_path' by a command in 'commands'")
        elif db(db.commands.parser_path.contains(db_rec.id)).count() == 0:
            db(db.devices.id == db_rec.id).delete()
            db.commit()
            logging.warning(f"Record id={db_rec.id} deleted from table 'command_parsers'")
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
        Method to load a command_parser object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'vendor' in json_data.keys() and json_data['vendor']:
            self.vendor = json_data['vendor'].strip().capitalize()
        if 'command' in json_data.keys() and json_data['command']:
            self.command = int(json_data['command'])
        if 'device_os' in json_data.keys() and json_data['device_os']:
            self.device_os = json_data['device_os'].lower()
        if 'is_json' in json_data.keys():
            self.is_json = json_data['is_json']
        if 'parser_path' in json_data.keys() and json_data['parser_path']:
            self.parser_path =  json_data['parser_path']
        if 'main_keys' in json_data.keys() and json_data['main_keys']:
            self.main_keys =  json_data['main_keys']
        if 'name' in json_data.keys() and json_data['name']:
            self.name =  json_data['name']
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
        return dict(id=self.db_id, vendor=self.vendor, command=self.command,
            device_os=self.device_os, is_json=self.is_json, parser_path=self.parser_path,
            main_keys=self.main_keys, name=self.name, created_at=self.created_at,
            modified_on=self.modified_on)
