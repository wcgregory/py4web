# coding: utf-8

import logging
import json

from pydal.objects import Row

from ..models import db
from .devices import DBDevice
from .commands import DBCommand
from .results import DBResult
from .command_parsers import DBParser

"""
>>> from apps.bcm.modules.result_reviewer import ResultsReview
>>> myreview = ResultsReview(22, 17)
>>> myreview.load_device()
>>> myreview.load_command()
>>> myreview.get_output_parser()
True
>>> myreview.results_comparison()
>>> myreview.report
>>> myreview.reviewed
True
>>> myreview.review_status
'Success'
>>> myreview.reviewed_at
'2024-09-08 21:51:58'

"""


class ResultsReview():
    """
    Mediator class to control 'result' object interactions
    """
    def __init__(self, current_result=None, previous_result=None):
        """
        Standard constructor class
        """
        self.device = None
        self.command = None
        self.output_parser = None
        self.current_result = DBResult(db_id=current_result)
        self.previous_result = DBResult(db_id=previous_result)
        self.reviewed = bool()
        self.reviewed_at = None
        self.review_status = None
        self.report = None
        self.comment = None
    
    @classmethod
    def get_results(cls, device=None):
        results_by_device = dict()
        if not device:
            results = db().select(db.results.ALL, orderby=db.results.device)
        else:
            if isinstance(device, int):
                results = db(db.results.device == device).select()
                results_by_device[device] = dict()
            if isinstance(device, str):
                dev = db((db.devices.mgmt_ip == device) | (db.devices.name == device)).select().first()
                results = db(db.results.device == dev.id).select()
                results_by_device[dev.id] = dict()
        #results_list = list()
        for res in results:
            r = DBResult(db_id=res.id)
            if not r.device in results_by_device.keys():
                results_by_device = {r.device: {res.id: r.to_json()}}
            else:
                results_by_device[r.device].update({res.id: r.to_json()})
        #results_list.append(results_by_device)
        return results_by_device
        #return results_list
    
    def load_result(self, result, current=True):
        """Create object and load the 'result' object or None"""
        if isinstance(result, int):
            res = DBResult(db_id=result)
        elif isinstance(result, Row):
            res = DBResult()
            res.load_by_id(db_rec=result)
        if not result:
            logging.warning(f"Expected 'result' object, received {type(result)}")
            return None
        if current:
            self.current_result = res
            logging.warning("Created and loaded a 'result' object as 'current_result'")
            self.device = self.load_device(device=self.current_result.device)
            self.command = self.load_command(command=self.current_result.command)
        else:
            if self.device and self.device.id != res.device:
                raise ValueError(self.__class__.__name__,
                    f"Device mismatch 'result' device id={res.device} and 'device' id={self.device.id}")
            if self.command and self.command.id != res.command:
                raise ValueError(self.__class__.__name__,
                    f"Command mismatch 'result' command id={res.command} and 'command' id={self.command.id}")
            self.previous_result = res
            logging.warning("Created and loaded a 'result' object as 'previous_result'")

    def load_device(self):
        """Create 'device' object and load details"""
        if (
            self.current_result and self.previous_result and 
            self.current_result.device == self.previous_result.device
        ):
            self.device = DBDevice(db_id=self.current_result.device)
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.device = None

    def load_command(self):
        """Create 'command' object and load details"""
        if (
            self.current_result and self.previous_result and 
            self.current_result.command == self.previous_result.command
        ):
            self.command = DBCommand(db_id=self.current_result.command)
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.command = None
    
    """
    def load_device(self, device):
        #Create object and load the 'device' object or None
        if isinstance(device, int):
            dev = DBDevice(db_id=device)
        elif isinstance(device, Row):
            dev = DBDevice()
            dev.load_by_id(db_rec=device)
        if not device:
            logging.warning(f"Expected 'device' object, received {type(device)}")
            return None
        if dev and isinstance(dev, DBDevice):
            self.device = dev
            logging.warning("Created and loaded a 'device' object for 'results_reviewer'")
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.device = None
    
    def load_command(self, command):
        #Create object and load the 'command' object or None
        if isinstance(command, int):
            command = DBCommand(db_id=command)
        elif isinstance(command, Row):
            command = DBCommand()
            command.load_by_id(db_rec=command)
        if not command:
            logging.warning(f"Expected 'command' object, received {type(command)}")
            return None
        if command and isinstance(command, DBCommand):
            logging.warning("Created and loaded a 'command' object for 'results_reviewer'")
            self.command = command
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.command = None
    """

    def get_output_parser(self):
        """Create object and load the 'command_parser' object or None"""
        if self.device and self.command:
            # search DB table 'command_parsers' matching by 'vendor', 'os' and 'command'
            query = (db.command_parsers.vendor == self.device.vendor) & (
                db.command_parsers.device_os == self.device.os)
            query &= (db.command_parsers.command == self.command.db_id)
            parser = db(query).select().first()
            if not parser:
                logging.warning(f"No parsers available")
                return False
            else:
                self.output_parser = DBParser(db_id=parser.id)
                return True
    
    def results_comparison(self):
        """
        Method to compare two 'result' classes 
        """
        if not self.current_result or not self.previous_result:
            raise ValueError(self.__class__.__name__, "Missing 'results' for comparison")  
        if not self.output_parser:
            self.get_output_parser()
        if not self.output_parser or not isinstance(self.output_parser, DBParser):
            raise TypeError(self.__class__.__name__, f"Expecting DBParser received {type(self.output_parser)}")  
        output_datapath = self.output_parser.parser_path
        cur_res_json = json.loads(self.current_result.result.replace("'", "\""))
        pre_res_json = json.loads(self.previous_result.result.replace("'", "\""))
        if len(output_datapath) == 1:
            cur_res = cur_res_json[output_datapath[0]]
            pre_res = pre_res_json[output_datapath[0]]
        elif len(output_datapath) == 2:
            cur_res = cur_res_json[output_datapath[0]][output_datapath[1]]
            pre_res = pre_res_json[output_datapath[0]][output_datapath[1]]
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
            self.report = {"last_report": pre_res, "current_report": cur_res}
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
            self.report = {"last_report": pre_res, "current_report": cur_res}
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
