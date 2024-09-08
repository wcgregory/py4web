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
        self.command = None
        self.output_parser = None
        #self.main_keys = None
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
        """Create object, load and return the 'result' object or None"""
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
    
    def load_device(self, device):
        """Create object and load the 'device' object or None"""
        if isinstance(device, int):
            device = DBDevice(db_id=device)
        elif isinstance(device, Row):
            device = DBDevice()
            device.load_by_id(db_rec=device)
        if not device:
            raise TypeError(self.__class__.__name__, f"Expected 'device' class, received {type(device)}")
        if device and isinstance(device, DBDevice):
            logging.warning("Created and loaded a 'device' object for 'results_reviewer'")
            self.device = device
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.device = None
    
    def get_output_parser(self):
        if self.device and self.command:
            query = db(db.command_parsers.vendor == self.device) & (
                db(db.command_parsers.device_os == self.device.os))
            query &= db(db.command_parsers.command == self.command)
            parser = db(query).select().first()
            if not parser:
                logging.warning(f"No parsers available")
                return False
            else:
                self.output_parser = DBParser(db_id=parser.id)
                #self.main_keys = parser.main_keys
                return True
    
    def results_comparison(self):
        """
        Method to compare two 'result' classes 
        """
        if not self.current_result or not self.previous_result:
            raise ValueError(self.__class__.__name__, "Missing 'results' for comparison")  
        if not self.output_parser:
            self.get_output_parser()
        if not self.output_parser and isinstance(self.output_parser, DBParser):
            raise TypeError(self.__class__.__name__, f"Expecting DBParser received {type(self.output_parser)}")  
        output_datapath = self.output_parser.parser_path
        if len(output_datapath) == 1:
            cur_res = self.current_result.result[output_datapath[0]]
            pre_res = self.current_result.result[output_datapath[0]]
        elif len(output_datapath) == 2:
            cur_res = self.current_result.result[output_datapath[0]][output_datapath[1]]
            pre_res = self.current_result.result[output_datapath[0]][output_datapath[1]]
        else:
            logging.warning(f"Need to add support when len > 2 for 'parser_path'")
            return False
        if cur_res == pre_res:
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Success'
            self.report = None
        #elif (cur_res and isinstance(cur_res, dict)) and (pre_res and isinstance(pre_res, dict)):
        elif isinstance(cur_res, dict) and isinstance(pre_res, dict):
            # add any differences from the results as a list of differences by key:value
            pre_diff = list({k:v} for k,v in pre_res.items() if not k in cur_res or v != cur_res[k])
            cur_diff = list({k:v} for k,v in cur_res.items() if not k in pre_res or v != pre_res[k])
            self.report = {"last_report": pre_diff, "current_report": cur_diff}
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Failed'
        #elif (cur_res and isinstance(cur_res, dict)) and (pre_res and isinstance(pre_res, list)):
        elif isinstance(cur_res, dict) and isinstance(pre_res, list):
            # add all differences due to result type mismatch
            self.report = {"last_report": pre_res, "current_report": list(cur_res)}
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
        #elif (cur_res and isinstance(cur_res, list)) and (pre_res and isinstance(pre_res, dict)):
        elif isinstance(cur_res, list) and pre_res and isinstance(pre_res, dict):
            # add all differences due to result type mismatch
            self.report = {"last_report": list(pre_res), "current_report": cur_res}
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Failed'
        #elif (cur_res and isinstance(cur_res, list)) and (pre_res and isinstance(pre_res, list)):
        elif isinstance(cur_res, list) and isinstance(pre_res, list):
            # add any differences from the results using set logic and provide as a list 
            pre_diff = list(set(pre_res) - set(cur_res))
            cur_diff = list(set(cur_res) - set(pre_res))
            self.report = {"last_report": pre_diff, "current_report": cur_diff}
            self.reviewed = True
            self.reviewed_at = self.current_result.get_timestamp()
            self.review_status = 'Failed'
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.reviewed = False
            self.review_status = 'Pending'
    
    def from_json(self, json_data):
        """
        Method to load a result_reviews object from a json data set.
        Must not set the DB id (db_id), if successful set self.json_import to True
        """
        if 'device' in json_data.keys() and json_data['device']:
            self.device = json_data['device']
        if 'command' in json_data.keys() and json_data['command']:
            self.command = json_data['command']
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
        return dict(device=self.device.name, command=self.command.syntax,
            current_result=self.current_result.id, previous_result=self.previous_result.id,
            reviewed=self.reviewed, reviewed_at=self.reviewed_at,
            review_status=self.review_status, report=self.report, comment=self.comment)
