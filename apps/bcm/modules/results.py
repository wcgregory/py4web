# coding: utf-8 #

import logging

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
