# coding: utf-8 #

import logging

from pydal.objects import Row

from .bcm_db import BCMDb
from ..models import db


class DBDevice(BCMDb):
    """
    DB Abstraction class for uniform interaction with DB Table 'devices'
    """
    def __init__(self, db_id=None, name=None, mgmt_ip=None):
        """
        Standard constructor class
        """
        super(DBDevice, self).__init__(db_id=db_id)
        #self._dbtable = 'devices' -> db.table == 'devices'
        self.name = name
        self.mgmt_ip = mgmt_ip
        self.vendor = None
        self.os = None
        self.device_function = None
        self.device_roles = list()
        self.commands = list()
        self.region = None
        self.site_code = None
        self.comment = None
        self.created_at = None
        self.modified_on = None
        if self.db_id:
            self.load_by_id()
    
    def load_by_id(self, db_rec=None, db_id=None):
        """
        Method to load a device object from the DB table using the DB id
        ---
        :param db_rec: a valid device DB record
        :type db_rec: pydal.objects.Row
        :param db_id: a valid device DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.devices.id == rec_id).select().first()
        if not db_rec:
            raise TypeError(self.__class__.__name__, f"Expecting record received {type(db_rec)}")
        self.db_id = db_rec.id
        self.name = db_rec.name
        self.mgmt_ip = db_rec.mgmt_ip
        self.vendor = db_rec.vendor
        self.os = db_rec.os
        self.device_function = db_rec.device_function
        self.device_roles = db_rec.device_roles
        self.commands = db_rec.commands
        self.region = db_rec.region
        self.site_code = db_rec.site_code
        self.comment = db_rec.comment
        self.created_at = db_rec.created_at
        self.modified_on = db_rec.modified_on
        self.db_loaded = True
    
    def save(self):
        """
        Save a record to DB - creator/updater method
        Must set the class db_id to the new DB id
        ---
        :return True or False: based on whether a new record is created or not
        """
        # create query to check whether record already exists 'name & mgmt_ip'
        query = (db.devices.name == self.name) & (db.devices.mgmt_ip == self.mgmt_ip)
        if db(query).count() == 0:
            # create query to check for duplicates of unique fields before save
            is_unique = (db.devices.name == self.name) | (db.devices.mgmt_ip == self.mgmt_ip)
            if db(is_unique).count() > 0:
                logging.warning(f"Duplicate value in 'devices' for name={self.name} or mgmt_ip={self.mgmt_ip}")
                return False
            self.created_at = DBDevice.get_timestamp()
            self.modified_on = self.created_at
            db.devices.insert(name=self.name, mgmt_ip=self.mgmt_ip, vendor=self.vendor,
                os=self.os, device_function=self.device_function, device_roles=self.device_roles,
                commands=self.commands, region=self.region, site_code=self.site_code,
                comment=self.comment, created_at=self.created_at, modified_on=self.modified_on)
            db.commit()
            db_rec = db(query).select().first()
            if db_rec:
                self.db_id = db_rec.id
                self.db_created = True
                logging.warning(f"New record created in table 'devices' id={self.db_id}")
                return True
        elif db(query).count() > 0:
            """
            TODO: This should be a modify record action.
                  We should not be able to update a duplicate entry.
            """
            db_rec = db(query).select().first()
            self.db_id = db_rec.id
            if not self.is_record_modified(db_rec=db_rec):
                logging.warning(f"No changes to save for id={self.db_id}")
                return False
            self.modified_on = DBDevice.get_timestamp()
            db.devices.update_or_insert(query,
                name=self.name, mgmt_ip=self.mgmt_ip, vendor=self.vendor, os=self.os,
                device_function=self.device_function, device_roles=self.device_roles,
                commands=self.commands, region=self.region, site_code=self.site_code,
                comment=self.comment, created_at=self.created_at, modified_on=self.modified_on)
            db.commit()
            logging.warning(f"Updated record in table 'devices' with id={self.db_id}")
            return True
        # catch-all error
        logging.warning("Unknown Error, more information/debugging required")
        db.rollback()
        return False
    
    def is_record_modified(self, db_rec=None, db_id=None):
        """
        Method to detect changes between class and DB record
        ---
        :param db_rec: a valid devices DB record
        :type db_rec: Row (pydal.objects.Row)
        :param db_id: a valid devices DB id
        :type db_id: int
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id()
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.devices.id == rec_id).select().first()
        elif db_rec and not isinstance(db_rec, Row):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting Row received {type(db_rec)}")
        if (
            self.vendor != db_rec.vendor or
            self.os != db_rec.os or
            self.device_function != db_rec.device_function or
            self.device_roles != db_rec.device_roles or
            self.commands != db_rec.commands or
            self.region != db_rec.region or
            self.site_code != db_rec.site_code or
            self.comment != db_rec.comment
        ):
            return True
        # catch-all
        return False

    def delete(self, db_rec=None, db_id=None):
        """
        Delete DB record - destructor method
        If successful switch value of self.db_created and self.db_loaded to False
        ---
        :return True or False: based on whether record is deleted or not
        """
        if db_rec is None:
            if db_id is None:
                rec_id = self.get_id(default=db_id)
            else:
                rec_id = db_id
            if not rec_id:
                raise ValueError(self.__class__.__name__, "Invalid or missing record id")
            db_rec = db(db.devices.id == rec_id).select().first()
        if not db_rec or (db_rec and not isinstance(db_rec, Row)):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting Row received {type(db_rec)}")
        if db(db.results.device.belongs(db(db.devices.id == db_rec.id).select())).count() == 0:
            db(db.devices.id == db_rec.id).delete()
            db.commit()
            logging.warning(f"Record deleted in table 'devices' with id={self.db_id}")
            self.db_id = None
            self.db_loaded = False
            self.db_created = False
            return True
        if db(db.results.device.belongs(db(db.devices.id == rec_id).select())).count() > 0:
            logging.warning(f"unable to delete device id={self.db_id} & name={self.name} while in 'results' table")
            return False
        # catch all error
        logging.warning("Unknown error, more information/debugging required")
        return False
    
    def from_json(self, json_data):
        """
        Method to load a devices object from a json data set.
        If successful set self.json_import to True
        Currently assumes no DB id - TODO: id and DB validation
        ---
        :param json_data: dict of parameters
        :type json_data: dict
        """
        if 'name' in json_data.keys():
            self.name = json_data['name'].strip()
        if 'mgmt_ip' in json_data.keys() and json_data['mgmt_ip']:
            self.mgmt_ip = json_data['mgmt_ip'].strip()
        if 'vendor' in json_data.keys() and json_data['vendor']:
            self.vendor = json_data['vendor'].strip().capitalize()
        if 'os' in json_data.keys() and json_data['os']:
            self.os = json_data['os'].strip().lower()
        if 'device_function' in json_data.keys() and json_data['device_function']:
            self.device_function = json_data['device_function'].strip().capitalize()
        if 'device_roles' in json_data.keys() and json_data['device_roles']:
            if isinstance(json_data['device_roles'], str):
                self.device_roles.append(json_data['device_roles'].strip().upper())
            elif isinstance(json_data['device_roles'], list):
                self.device_roles = [role.strip().upper() for role in json_data['device_roles']]
        if 'commands' in json_data.keys() and json_data['commands']:
            self.commands = json_data['commands']
        if 'region' in json_data.keys() and json_data['region']:
            self.region = json_data['region'].strip().upper()
        if 'site_code' in json_data.keys() and json_data['site_code']:
            self.site_code = json_data['site_code'].strip().upper()
        if 'comment' in json_data.keys() and json_data['comment']:
            self.comment = json_data['comment'].strip()
        if 'created_at' in json_data.keys() and json_data['created_at']:
            self.created_at = json_data['created_at']
        if 'modified_on' in json_data.keys() and json_data['modified_on']:
            self.modified_on = json_data['modified_on']
        self.json_import = True
    
    def to_json(self):
        """
        Returns class attributes in dict format.
        ---
        :return: class attributes as dict
        """
        return dict(id=self.db_id, name=self.name, mgmt_ip=self.mgmt_ip, vendor=self.vendor,
            os=self.os, device_function=self.device_function, device_roles=self.device_roles,
            commands=self.commands, region=self.region, site_code=self.site_code,
            comment=self.comment, created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            modified_on=self.modified_on.strftime("%Y-%m-%d %H:%M:%S"))


class DBDevices():
    """
    DB Abstraction class for uniform interaction with lists of 'devices'
    """
    def __init__(self, db_ids=None):
        """
        Standard constructor class
        """
        #self._dbtable = 'devices' -> db.tables == 'devices'
        self.db_ids = db_ids
        self.devices = list()
    
    @staticmethod
    def get_devices(db_ids=None):
        if not db_ids:
            devices = db(db.devices).select()
        else:
            if isinstance(db_ids, list):
                for db_id in db_ids:
                    idx = 0
                    while idx < len(db_ids):
                        if idx == 0:
                            query = (db.devices.id == db_id)
                        else:
                            query |= (db.devices.id == db_id)
                        idx += 1
                devices = db(query).select()
        devices_list = []
        for device in devices:
            d = DBDevice(db_id=device.id)
            devices_list.append(d.to_json())
        return devices_list
