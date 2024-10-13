# coding: utf-8

import logging
import json

from pydal.objects import Row

from .bcm_db import BCMDb
from .network_poller import NetworkPoller
from ..models import db, COMMAND_STATUSES


class DBJob(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'jobs'
    """
    def __init__(self, db_id=None, name=None, comment=None):
        """
        Standard constructor class
        """
        super(DBJob, self).__init__(db_id=db_id)
        #self._dbtable = 'jobs' -> db.tables == 'jobs'
        self.name = name
        self.devices = list()
        self.results = list()
        self.started_at = DBJob.get_timestamp()
        self.completed_at = None
        self.status = "Pending"
        self.comment = comment
        if self.db_id:
            self.load_by_id()
        # credentials should not be stored in DB, only used at runtime
        self.runtime = None
    
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
    
    def set_devices(self, devices):
        if isinstance(devices, int) and db(db.devices.id == devices).count() == 1:
            self.devices = list(devices)
        if isinstance(devices, list):
            no_id = [device for device in devices if not db(db.devices.id == device).count() == 1]
            if no_id:
                raise ValueError(self.__class__.__name__, f"No DB id found for 'devices' {no_id}")
            else:
                self.devices = devices
    
    def set_name(self, name=None):
        if not self.name:
            self.name = name if name else f"job_{db(db.jobs).select().last().id + 1}"

    def update_name(self, name=None):
        self.name = name if name else f"job_{db(db.jobs).select().last().id + 1}"
    
    def update_status(self, status):
        if status.capitalize() in COMMAND_STATUSES:
            self.status = status.capitalize()
    
    def set_runtime_account(self, credentials):
        self.runtime = dict()
        self.runtime.update({"auth": credentials})
    
    def save(self):
        """
        Save a job to DB - creator method
        Must set the class db_id to the new DB id
        ---
        :return True or False: based on whether a new job is created or not
        """
        if not self.name:
            logging.warning("No 'jobs' name provided for 'save' method")
            return False
        # create query to check whether 'jobs' name already exists
        query = (db.jobs.name == self.name)
        if db(query).count() > 0:
            logging.warning(f"Duplicate 'jobs' name {self.name} use 'update' method")
            return False
        else:
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
    
    def update(self):
        """
        Update a job to DB - updater method
        ---
        :return True or False: based on whether the 'job is updated
        """
        if db(db.jobs.id == self.db_id).count() == 0:
            return self.save()
        else:
            db_rec = db(db.jobs.id == self.db_id).select().first()
            if not self.is_record_modified(db_rec=db_rec):
                logging.warning(f"No changes to save for id={self.db_id}")
                return False
            query = (db.jobs.id == self.db_id) & (db.jobs.name == self.name)
            query &= (db.jobs.devices == self.devices) & (db.jobs.started_at == self.started_at)
            db.jobs.update_or_insert(query,
                results=self.results, completed_at=self.completed_at,
                status=self.status, comment=self.comment)
            db.commit()
            logging.warning(f"Updated record in table 'jobs' id={self.db_id}, name={self.name}")
            return False
    
    def is_record_modified(self, db_rec=None, db_id=None):
        """
        Method to detect changes between class and DB record
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
        elif db_rec and not isinstance(db_rec, Row):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting Row received {type(db_rec)}")
        if (
            self.results != db_rec.results or
            self.completed_at != db_rec.completed_at or
            self.status != db_rec.status or
            self.comment != db_rec.comment
        ):
            return True
        # catch-all
        logging.warning("Unknown Error 'jobs:is_record_modified', more information/debugging required")
        return False
    
    def run(self):
        self.update_status(status="Running")
        for device in self.devices:
            j_np = NetworkPoller(device_id=device, job_id=self.db_id)
            j_np.load_device_commands()
            if device == 4:
                self.set_runtime_account(credentials=('admin', 'C1sco12345'))
            elif device == 5:
                self.set_runtime_account(credentials=('admin', 'Admin_1234!'))
            #print(device)
            j_np.run_device_commands(auth=self.runtime.get('auth'))
            j_np.save_results()
            self.results.extend(list(j_np.results))
        self.completed_at = DBJob.get_timestamp()
        self.update_status(status="Completed")
        self.update()
    
    def from_json(self, json_data):
        """
        Method to load a jobs object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'name' in json_data.keys() and json_data['name']:
            self.name =  json_data['name'].strip()
        self.devices = json_data.get('devices', list())
        self.results = json_data.get('results', list())
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
