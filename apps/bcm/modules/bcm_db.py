# coding: utf-8 #

from datetime import datetime


class BCMDb(object):
    """
    Base DB Abstraction class for uniform interaction with DB Tables
    """
    def __init__(self, db_id=None):
        self.db_id = db_id
        self.db_loaded = False
        self.db_created = False
        self.json_import = False
    
    def get_id(self, default=None):
        """Return the class DB id"""
        return self.db_id if self.db_id else default
    
    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate(self):
        """
        Check the validity of the class.
        Raise DataValidationError if validation fails, otherwise return nothing or true.
        ---
        return: Nothing or True
        """
        raise NotImplemented()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Class loader from DB Tables.
        Populates the attributes of the class from the db, by record data or by id.
        If successful switch value of self.db_loaded to True
        """
        raise NotImplemented()
    
    def from_json(self, json_data):
        """
        Class import loader.
        Import data and populate the class attributes, must not set the DB id (db_id)
        If successful switch value of self.json_import to True
        """
        raise NotImplemented()

    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        raise NotImplemented()
    
    def set_db_record(self):
        """
        Class to DB record creator
        Must not have or use a class db_id, a DB id will be created
        ---
        :return True or False: based on whether a new record is created or not
        """
        raise NotImplemented()
