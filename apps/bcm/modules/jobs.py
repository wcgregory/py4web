# coding: utf-8

import logging
import json

from pydal.objects import Row

from .bcm_db import BCMDb
from ..models import db


class DBJob(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'jobs'
    """
    def __init__(self, db_id=None):
        """
        Standard constructor class
        """
        super(DBJob, self).__init__(db_id=db_id)
        #self._dbtable = 'jobs' -> db.tables == 'jobs'
        self.name = None
        self.devices = list()
        self.results = list()
        self.started_at = None
        self.completed_at = None
        self.status = None
        self.comment = None
        if self.db_id:
            self.load_by_id()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a jobs object from the DB table using the DB id
        ---
        :param db_rec: a valid jobs DB record
        :type db_rec: Row (pydal.objects.Row)
        :param db_id: a valid jobs DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.jobs.id == rec_id).select().first()    
        if not db_rec:
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        self.name = db_rec.name
        self.devices = db_rec.devices
        self.results = db_rec.results
        self.started_at = db_rec.started_at
        self.completed_at = db_rec.completed_at
        self.status = db_rec.status
        self.comment = db_rec.comment
        self.db_loaded = True
    
    def save(self):
        """
        Save a record to DB - creator/updater method
        Must set the class db_id to the new DB id
        ---
        :return True or False: based on whether a new record is created or not
        """
        # create query to check whether 'jobs' name already exists
        query = (db.jobs.name == self.name)
        if db(query).count() > 0:
            logging.warning(f"Duplicate 'name' exists in 'jobs' table for name={self.name}")
            return False
        elif db(query).count() == 0:
            db.jobs.insert(name=self.name, devices=self.devices, results=self.results,
                started_at=self.started_at, completed_at=self.completed_at,
                status=self.status, comment=self.comment)
            db.commit()
            db_rec = db(query).select().first()
            if db_rec:
                self.db_id = db_rec.id
                self.db_created = True
                logging.warning(f"New record created in table 'jobs' id={self.db_id}")
                return True
        # catch-all error
        logging.warning("Unknown Error, more information/debugging required")
        db.rollback()
        return False

    def from_json(self, json_data):
        """
        Method to load a jobs object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'name' in json_data.keys() and json_data['name']:
            self.name =  json_data['name'].strip()
        if 'devices' in json_data.keys() and json_data['devices']:
            self.devices = json_data['devices']
        if 'results' in json_data.keys() and json_data['command']:
            self.command = json_data['command']
        if 'started_at' in json_data.keys() and json_data['started_at']:
            self.started_at = json_data['started_at'].strip()
        if 'completed_at' in json_data.keys() and json_data['completed_at']:
            self.completed_at = json_data['completed_at'].strip()
        if 'status' in json_data.keys() and json_data['status']:
            self.status = json_data['status'].strip().capitalize()
        if 'comment' in json_data.keys() and json_data['comment']:
            self.comment =  json_data['comment'].strip()
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, name=self.name,
            devices=self.devices, results=self.results,
            started_at=self.started_at.strftime("%Y-%m-%d %H:%M:%S"),
            completed_at=self.completed_at.strftime("%Y-%m-%d %H:%M:%S"),
            status=self.status, rcomment=self.comment)


class DBJobs():
    """
    DB Abstraction class for uniform interaction with lists of 'jobs'
    """
    def __init__(self, db_ids=None):
        """
        Standard constructor class
        """
        #self._dbtable = 'jobs' -> db.tables == 'jobs'
        self.db_ids = db_ids
        self.jobs = list()
    
    @staticmethod
    def get_jobs(db_ids=None):
        if not db_ids:
            jobs = db(db.jobs).select()
        else:
            if isinstance(db_ids, list):
                for db_id in db_ids:
                    idx = 0
                    while idx < len(db_ids):
                        if idx == 0:
                            query = (db.jobs.id == db_id)
                        else:
                            query |= (db.jobs.id == db_id)
                        idx += 1
                jobs = db(query).select()
        jobs_list = []
        for job in jobs:
            j = DBJob(db_id=job.id)
            jobs_list.append(j.to_json())
        return jobs_list
