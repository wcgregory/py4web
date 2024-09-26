# coding: utf-8 #

import logging
import json

from pydal.objects import Row

from .bcm_db import BCMDb
from ..models import db


class DBResult(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'results'
    """
    def __init__(self, db_id=None):
        """
        Standard constructor class
        """
        super(DBResult, self).__init__(db_id=db_id)
        #self._dbtable = 'results' -> db.tables == 'results'
        self.device = None
        self.command = None
        self.completed_at = None
        self.status = None
        self.result = None
        self.last_result = None
        self.comment = None
        if self.db_id:
            self.load_by_id()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a results object from the DB table using the DB id
        ---
        :param db_rec: a valid results DB record
        :type db_rec: Row (pydal.objects.Row)
        :param db_id: a valid results DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.results.id == rec_id).select().first()    
        if not db_rec:
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        self.device = db_rec.device
        self.command = db_rec.command
        self.completed_at = db_rec.completed_at
        self.status = db_rec.status
        self.result = db_rec.result
        self.last_result = db_rec.last_result
        self.comment = db_rec.comment
        self.db_loaded = True
    
    def save(self):
        """
        Save a record to DB - creator/updater method
        Must set the class db_id to the new DB id
        ---
        :return True or False: based on whether a new record is created or not
        """
        # create query to check whether 'device' has run 'command' before
        query = (db.results.device == self.device) & (db.results.command == self.command)
        if db(query).count() > 0:
            db_last_rec = db(query).select().last()
            if db_last_rec and isinstance(db_last_rec, Row):
                self.last_result = db_last_rec.id
        # add to query to check key field 'completed_at' for uniqueness
        query &= (db.results.completed_at == self.completed_at)
        # ensure result is saved as a JSON blob
        # self.result = json.dumps(self.result.replace("'", "\""))
        if db(query).count() == 0:
            db.results.insert(device=self.device, command=self.command,
                completed_at=self.completed_at, status=self.status,
                result=self.result, last_result=self.last_result,
                comment=self.comment)
            db.commit()
            db_rec = db(query).select().first()
            if db_rec:
                self.db_id = db_rec.id
                self.db_created = True
                logging.warning(f"New record created in table 'results' id={self.db_id}")
                return True
        elif db(query).count() > 0:
            db_rec = db(query).select().first()
            self.db_id = db_rec.id
            logging.warning(f"Record exists in table 'results' id={self.db_id} - no updates permitted")
            return False
        # catch-all error
        logging.warning("Unknown Error, more information/debugging required")
        db.rollback()
        return False

    def from_json(self, json_data):
        """
        Method to load a device object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'device' in json_data.keys() and json_data['device']:
            self.device = int(json_data['device'])
        if 'command' in json_data.keys() and json_data['command']:
            self.command = int(json_data['command'])
        if 'completed_at' in json_data.keys() and json_data['completed_at']:
            self.completed_at = json_data['completed_at'].strip()
        if 'status' in json_data.keys() and json_data['status']:
            self.status = json_data['status'].strip().capitalize()
        if 'result' in json_data.keys() and json_data['result']:
            self.result = json_data['result']
        if 'last_result' in json_data.keys() and json_data['last_result']:
            self.last_result = int(json_data['last_result'])
        if 'comment' in json_data.keys() and json_data['comment']:
            self.comment =  json_data['comment'].strip()
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, device=self.device, command=self.command,
                completed_at=self.completed_at.strftime("%Y-%m-%d %H:%M:%S"),
                status=self.status, result=self.result,
                last_result=self.last_result, comment=self.comment)


class DBResults():
    """
    DB Abstraction class for uniform interaction with lists of 'results'
    """
    def __init__(self, db_ids=None):
        """
        Standard constructor class
        """
        #self._dbtable = 'results' -> db.tables == 'results'
        self.db_ids = db_ids
        self.results = list()
    
    @staticmethod
    def get_results(db_ids=None):
        if not db_ids:
            results = db(db.results).select()
        else:
            if isinstance(db_ids, list):
                for db_id in db_ids:
                    idx = 0
                    while idx < len(db_ids):
                        if idx == 0:
                            query = (db.results.id == db_id)
                        else:
                            query |= (db.results.id == db_id)
                        idx += 1
                results = db(query).select()
        results_list = []
        for result in results:
            r = DBResult(db_id=result.id)
            results_list.append(r.to_json())
        return results_list
