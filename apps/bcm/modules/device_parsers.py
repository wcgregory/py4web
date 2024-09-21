# coding: utf-8

from ..models import db
from .bcm_db import BCMDb
from .commands import DBCommand


class Parser(BCMDb):
    def __init__(self):
        self.vendor = None
        self.commands = None
    
    def load_vendor_commands(self):
        db_row_cmds = db(db.commands.vendors.contains(self.vendor)).select()
        self.commands = [{cmd.syntax: {}} for cmd in db_row_cmds]
    
    def add_output_parser(self, command, parser):
        if command in self.commands.keys():
            self.commands.update(parser)


class AristaParser(Parser):
    def __init__(self):
        super(AristaParser, self).__init__()
        self.vendor = 'Arista'
        self.commands = None


class CiscoIOSParser(Parser):
    def __init__(self):
        pass


class CiscoNXOSParser(Parser):
    def __init__(self):
        pass
    
    # # 'TABLE_intf': {'ROW_intf': []


class JuniperParser(Parser):
    def __init__(self):
        pass