# coding: utf-8

import logging

from pydal.objects import Row

from ..models import db
from .devices import DBDevice
from .results import DBResult
from .command_parsers import DBParser
#from .device_parsers import CiscoNXOSParser


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
        self.output_parser = None
        self.main_keys = None
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
    
    def get_output_parser(self):
        if self.device and self.device_os and self.command:
            query = db(db.command_parsers.vendor == self.device) & (
                db(db.command_parsers.device_os == self.device_os))
            query &= db(db.command_parsers.command == self.command)
            parser = db(query).select().first()
            if not parser:
                logging.warning(f"No parsers available")
                return False
            else:
                self.output_parser = parser.parser_path
                self.main_keys = parser.main_keys
                return True
    
    def results_comparison(self):
        """
        Method to compare two 'result' classes 
        """
        if not self.current_result or not self.previous_result:
            raise ValueError(self.__class__.__name__, f"Missing 'results' for comparison")  
        if not self.output_parser:
            self.get_output_parser()
        if len(self.output_parser) == 1:
            cur_res = self.current_result.result[self.output_parser[0]]
            pre_res = self.current_result.result[self.output_parser[0]]
        elif len(self.output_parser) == 2:
            cur_res = self.current_result.result[self.output_parser[0]][self.output_parser[1]]
            pre_res = self.current_result.result[self.output_parser[0]][self.output_parser[1]]
        else:
            logging.warning(f"Need to add support when len > 2 for 'parser_path'")
            return False
        if cur_res == pre_res:
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Success'
            self.report = None
        elif (cur_res and isinstance(cur_res, dict)) and (pre_res and isinstance(pre_res, dict)):
            # add any dict differences from the results as a list of differences by key:value
            self.report = list({(k, v) for (k, v) in pre_res.items() if k in cur_res and v == cur_res[k]})
            self.report.extend({(k, v) for (k, v) in cur_res.items() if k in pre_res and v == pre_res[k]})
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Failed'
        elif (cur_res and isinstance(cur_res, dict)) and (pre_res and isinstance(pre_res, list)):
            self.report = list(cur_res)
            self.report.extend(pre_res)
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Failed'
            """
                if self.main_keys:
                # create a searchable dict using the main keys to match each dict in list
                dict_search = {k:v for k,v in cur_res.items() if k in self.main_keys}
                for result in pre_res:
                    res_match = {k:v for k,v in result.items() if k in self.main_keys}
                    if dict_search == res_match and cur_res == result:
                        self.reviewed = True
                        self.reviewed_at = self.current_result.get_timestamp()
                        self.review_status = 'Failed'
                        self.report = None
            """
        elif (cur_res and isinstance(cur_res, list)) and (pre_res and isinstance(pre_res, list)):
            cur_diff = list(set(cur_res) - set(pre_res))
            pre_diff = list(set(pre_res) - set(cur_res))
            self.report = cur_diff + pre_diff
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Failed'
        elif (cur_res and isinstance(cur_res, list)) and (pre_res and isinstance(pre_res, dict)):
            pass
    
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
