# coding: utf-8 #

import logging

from .bcm_db import BCMDb
from ..models import db


class DBResult(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'devices'
    """
    def __init__(self, db_id=None):
        """
        Standard constructor class
        """
        super(DBResult, self).__init__(db_id=db_id)
        pass
