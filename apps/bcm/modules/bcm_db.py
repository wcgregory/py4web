# coding: utf-8 #


class BCMDb(object):
    """
    Base DB Abstraction class for uniform interaction with DB Tables
    """
    def __init__(self, db_id=None):
        self.db_id = db_id
        self.db_loaded = False
    
    def get_id(self):
        return self.db_id
    
    def validate(self):
        """
        """
        raise NotImplemented()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        """
        raise NotImplemented()
    
    def from_json(self, json_data):
        """
        """
        raise NotImplemented()

    def to_json(self):
        """
        """
        raise NotImplemented()
