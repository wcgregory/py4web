# coding: utf-8

import logging
import json

from pydal.objects import Row

from ..models import db
from .devices import DBDevice
from .commands import DBCommand
from .results import DBResult
from .output_parsers import DBParser

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
    def __init__(self, result_one=None, result_two=None):
        """
        Standard constructor class
        """
        self.device = None
        self.command = None
        self.output_parser = None
        self.result_one = DBResult(db_id=result_one)
        self.result_two = DBResult(db_id=result_two)
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
        for res in results:
            r = DBResult(db_id=res.id)
            d = DBDevice(db_id=r.device)
            c = DBCommand(db_id=r.command)
            if not r.device in results_by_device.keys():
                results_by_device.update({r.device: {res.id: r.to_json()}})
            else:
                results_by_device[r.device].update({res.id: r.to_json()})
            results_by_device[r.device][res.id].update({"device_name": d.name})
            results_by_device[r.device][res.id].update({"command_name": c.syntax})
        return results_by_device
    
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
            self.result_one = res
            logging.warning("Created and loaded a 'result' object as 'result_one'")
            self.device = self.load_device(device=self.result_one.device)
            self.command = self.load_command(command=self.result_one.command)
        else:
            if self.device and self.device.id != res.device:
                raise ValueError(self.__class__.__name__,
                    f"Device mismatch 'result' device id={res.device} and 'device' id={self.device.id}")
            if self.command and self.command.id != res.command:
                raise ValueError(self.__class__.__name__,
                    f"Command mismatch 'result' command id={res.command} and 'command' id={self.command.id}")
            self.result_two = res
            logging.warning("Created and loaded a 'result' object as 'result_two'")

    def load_device(self):
        """Create 'device' object and load details"""
        if (
            self.result_one and self.result_two and 
            self.result_one.device == self.result_two.device
        ):
            self.device = DBDevice(db_id=self.result_one.device)
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.device = None

    def load_command(self):
        """Create 'command' object and load details"""
        if (
            self.result_one and self.result_two and 
            self.result_one.command == self.result_two.command
        ):
            self.command = DBCommand(db_id=self.result_one.command)
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.command = None
    
    def get_output_parser(self):
        """Create object and load the 'output_parsers' object or None"""
        if self.device and self.command:
            # search DB table 'output_parsers' matching by 'vendor', 'os' and 'command'
            query = (db.output_parsers.vendor == self.device.vendor) & (
                db.output_parsers.device_os == self.device.os)
            query &= (db.output_parsers.command == self.command.db_id)
            parser = db(query).select().first()
            if not parser:
                logging.warning(f"No parsers available for command id={self.command.db_id}")
            else:
                self.output_parser = DBParser(db_id=parser.id)
    
    def results_comparison(self):
        """
        Method to compare two 'DBResult' classes 
        """
        if not self.result_one or not self.result_two:
            raise ValueError(self.__class__.__name__, "Missing 'results' for comparison")  
        if not self.output_parser:
            self.get_output_parser()
        if not self.output_parser or not isinstance(self.output_parser, DBParser):
            raise TypeError(self.__class__.__name__, f"Expecting DBParser received {type(self.output_parser)}")  
        output_datapath = self.output_parser.parser_path
        res_j_one = json.loads(self.result_one.result)
        res_j_two = json.loads(self.result_two.result)
        if not output_datapath:
            res_one = res_j_one
            res_two = res_j_two
        elif len(output_datapath) == 1:
            res_one = res_j_one[output_datapath[0]]
            res_two = res_j_two[output_datapath[0]]
        elif len(output_datapath) == 2:
            res_one = res_j_one[output_datapath[0]][output_datapath[1]]
            res_two = res_j_two[output_datapath[0]][output_datapath[1]]
        else:
            logging.warning(f"Need to add support when len > 2 for 'parser_path'")
            return False
        if res_one == res_two:
            self.reviewed = True
            self.reviewed_at = self.result_one.get_timestamp()
            self.review_status = 'Success'
            self.report = None
        #elif (res_one and isinstance(res_one, dict)) and (res_two and isinstance(res_two, dict)):
        elif isinstance(res_one, dict) and isinstance(res_two, dict):
            # add any differences from the results as a list of differences by key:value
            diff_one = list({k:v} for k,v in res_two.items() if not k in res_one or v != res_one[k])
            diff_two = list({k:v} for k,v in res_one.items() if not k in res_two or v != res_two[k])
            self.report = {"last_report": diff_one, "current_report": diff_two}
            self.reviewed = True
            self.reviewed_at = self.result_one.get_timestamp()
            self.review_status = 'Failed'
        #elif (res_one and isinstance(res_one, dict)) and (res_two and isinstance(res_two, list)):
        elif isinstance(res_one, dict) and isinstance(res_two, list):
            # add all differences due to result type mismatch
            self.report = {"last_report": res_two, "current_report": res_one}
            self.reviewed = True
            self.reviewed_at = self.result_one.get_timestamp()
            self.review_status = 'Failed'
            """
                if self.main_keys:
                # create a searchable dict using the main keys to match each dict in list
                dict_search = {k:v for k,v in res_one.items() if k in self.main_keys}
                for result in res_two:
                    res_match = {k:v for k,v in result.items() if k in self.main_keys}
                    if dict_search == res_match and res_one == result:
                        self.reviewed = True
                        self.reviewed_at = self.result_one.get_timestamp()
                        self.review_status = 'Failed'
                        self.report = None
            """
        #elif (res_one and isinstance(res_one, list)) and (res_two and isinstance(res_two, dict)):
        elif isinstance(res_one, list) and res_two and isinstance(res_two, dict):
            # add all differences due to result type mismatch
            self.report = {"last_report": res_two, "current_report": res_one}
            self.reviewed = True
            self.reviewed_at = self.result_one.get_timestamp()
            self.review_status = 'Failed'
        #elif (res_one and isinstance(res_one, list)) and (res_two and isinstance(res_two, list)):
        elif (isinstance(res_one, list) and isinstance(res_two, list)):
            if (
                len(res_one) == 1 and isinstance(res_one[0], dict) and
                len(res_two) == 1 and isinstance(res_two[0], dict)
            ):
                diff_one = list(
                    {k:v} for k,v in res_two[0].items() if not k in res_one[0] or v != res_one[0][k]
                )
                diff_two = list(
                    {k:v} for k,v in res_one[0].items() if not k in res_two[0] or v != res_two[0][k]
                )
            else:
                # add any differences from the results using set logic and provide as a list
                diff_one = list(set(res_one) - set(res_two))
                diff_two = list(set(res_two) - set(res_one))
            self.report = {"last_report": diff_two, "current_report": diff_one}
            self.reviewed = True
            self.reviewed_at = self.result_one.get_timestamp()
            self.review_status = 'Failed'
        else:
            # catch-all error
            logging.warning("Unknown Error, more information/debugging required")
            self.reviewed = False
            self.review_status = 'Pending'
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(device=self.device.name, command=self.command.syntax,
            result_one=self.result_one.db_id, result_two=self.result_two.db_id,
            reviewed=self.reviewed, reviewed_at=self.reviewed_at,
            review_status=self.review_status, report=self.report, comment=self.comment)
