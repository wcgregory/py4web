# coding: utf-8

import logging

from pydal.objects import Row

from ..models import db
from .devices import DBDevice
from .results import DBResult
from .device_parsers import CiscoNXOSParser

class ResultsReview():
    """
    Abstraction class for uniform interaction for reviewing and comparing db results
    """
    def __init__(self, current_result=None, previous_result=None):
        """
        Standard constructor class
        """
        self.device = None
        self.device_os = None
        self.command = None
        if current_result:
            self.current_result = self.load_result(result=current_result)
        if previous_result:
            self.previous_result = self.load_result(result=previous_result)
        self.reviewed = bool()
        self.reviewed_at = None
        self.review_status = None
        self.report = None
        self.comment = None
    
    def load_result(self, result):
        """Create, load and return a 'result' object or None"""
        if isinstance(result, int):
            result = DBResult(db_id=result)
        elif isinstance(result, Row):
            result = DBResult()
            result.load_by_id(db_rec=result)
        if not result:
            raise TypeError(self.__class__.__name__, f"Expected 'result' class, received {type(result)}")
        if self.device and self.device != result.device:
            raise ValueError(self.__class__.__name__, f"Device mismatch id={result.device} and id={self.device}")  
        if self.command and result.command != self.command:
            raise ValueError(self.__class__.__name__, f"Command mismatch id={result.command} and id={self.command}")
        self.device = result.device
        self.command = result.command
        return result
    
    def get_device_os(self):
        if self.device:
            d = DBDevice(db_id=self.device)
        self.device_os = d.os
    
    def results_comparison(self):
        """
        Method to compare two 'result' classes 
        """
        if self.device == 'Cisco' and self.device_os == 'nxos':
            parser = CiscoNXOSParser()
            parser.add_command_parser()
            # 'TABLE_intf': {'ROW_intf': []
        self.review_status = 'Running'
        cur_res = None
        pre_res = None
    
    def from_json(self, json_data):
        """
        Method to load a result_reviews object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'device' in json_data.keys() and json_data['device']:
            self.device = int(json_data['device'])
        if 'current_result' in json_data.keys() and json_data['current_result']:
            self.current_result = json_data['current_result']
        if 'previous_result' in json_data.keys() and json_data['previous_result']:
            self.previous_result = json_data['previous_result']
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
        return dict(device=self.device, current_result=self.current_result.id,
            previous_result=self.previous_result.id, reviewed=self.reviewed,
            reviewed_at=self.reviewed_at, review_status=self.review_status,
            report=self.report, comment=self.comment)
