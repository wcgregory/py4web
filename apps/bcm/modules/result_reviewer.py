# coding: utf-8

import logging

from pydal.objects import Row

from .bcm_db import BCMDb
from ..models import db


class ResultsReview(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'result_reviews'
    """
    def __init__(self, db_id=None):
        """
        Standard constructor class
        """
        self.current_result = None
        self.last_result = None
        self.reviewed = bool()
        self.reviewed_at = None
        self.review_status = None
        self.report = None
        self.comment = None
        if self.db_id:
            self.load_by_id()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a result_reviews object from the DB table using the DB id
        ---
        :param db_rec: a valid result_reviews DB record
        :type db_rec: Row (pydal.objects.Row)
        :param db_id: a valid result_reviews DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.result_reviews.id == rec_id).select().first()
        if not db_rec:
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        self.current_result = db_rec.current_result
        self.last_result = db_rec.last_result
        self.reviewed = db_rec.reviewed
        self.reviewed_at = db_rec.reviewed_at
        self.review_status = db_rec.review_status
        self.report = db_rec.report
        self.comment = db_rec.comment
        self.db_loaded = True
    
    def save(self):
        """
        Save a record to DB - creator/updater method
        Must set the class db_id to the new DB id
        ---
        :return True or False: based on whether a new record is created or not
        """
        pass
    
    def from_json(self, json_data):
        """
        Method to load a result_reviews object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'current_result' in json_data.keys() and json_data['current_result']:
            self.current_result = int(json_data['current_result'])
        if 'last_result' in json_data.keys() and json_data['last_result']:
            self.last_result = int(json_data['last_result'])
        if 'reviewed' in json_data.keys() and json_data['reviewed']:
            self.reviewed = json_data['reviewed']
        if 'reviewed_at' in json_data.keys() and json_data['reviewed_at']:
            self.reviewed_at = json_data['reviewed_at'].strip()
        if 'review_status' in json_data.keys() and json_data['review_status']:
            self.review_status = json_data['review_status'].strip().capitalize()
        if 'report' in json_data.keys() and json_data['report']:
            self.report = json_data['report'].strip()
        if 'comment' in json_data.keys() and json_data['comment']:
            self.comment =  json_data['comment'].strip()
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, current_result=self.current_result,
            last_result=self.last_result, reviewed=self.reviewed,
            reviewed_at=self.reviewed_at, review_status=self.review_status,
            report=self.report, comment=self.comment)
