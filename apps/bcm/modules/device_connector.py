# coding: utf-8 #

import logging
import os
import re
import json

from netmiko import NetmikoTimeoutException
from paramiko.ssh_exception import AuthenticationException, SSHException
from netmiko.ssh_dispatcher import ConnectHandler



class NetmikoConnect():
    """
    Netmiko ConnectHandler wrapper class
    """
    def __init__(self, host=None, vendor=None):
        self.vendor = vendor
        self.host = host
        self.username = None
        self.password = None
        self.connect = None
        self.is_connected = False
        if self.vendor:
            self.device_type = self.set_netmiko_device_type(vendor=self.vendor)
    
    def set_username(self, username):
        self.username = username
    
    def set_password(self, password):
        self.password = password
    
    def set_netmiko_device_type(self, vendor=None):
        """Set netmiko device_type based on vendor"""
        if not vendor and not self.vendor:
            raise ValueError(self.__class__.__name__, "Invalid or missing vendor of host")
        else:
            self.vendor = vendor.strip().capitalize()
        if self.vendor == 'Arista':
            self.device_type = 'arista_eos'
        elif self.vendor == 'Cisco':
            self.device_type = 'cisco_ios'
        elif self.vendor == 'Juniper':
            self.device_type = 'juniper_junos'
        else:
            self.device_type = 'unknown'
    
    def connect_to_device(self, auth=None):
        """Connect to the host device"""
        if self.is_connected:
            logging.warning(self.__class__.__name__, "Already connected")
            return False
        if not self.username and not isinstance(auth, tuple):
            logging.warning(self.__class__.__name__, "No login credentials set")
            return False
        elif auth and isinstance(auth, tuple):
            self.username = auth[0]
            self.password = auth[1]
        device_params = {"host": self.host, "device_type": self.device_type, "username": self.username,
            "password": self.password}
        if self.device_type == 'juniper_junos':
            device_params.update({"fast_cli": False})
        try:
            self.connect = ConnectHandler(**device_params)
        except (NetmikoTimeoutException):
            logging.warning(self.__class__.__name__, "No response, connection timed out!")
        except (AuthenticationException):
            logging.warning(self.__class__.__name__, "No login credentials set!")
        except (SSHException):
            logging.warning(self.__class__.__name__, "SSH issue!")
        except Exception as unknown_error:
            logging.warning(self.__class__.__name__, "Unexpected error!")
        if self.connect and self.connect.is_alive():
            self.is_connected = True

    def send_op_command(self, cmd, timing=False):
        """
        Send op command and return output
        """
        if cmd and isinstance(cmd, str):
            command = cmd
        else:
            raise TypeError(self.__class__.__name__, f"Invalid type expecting str received {type(command)}")
        if not self.is_connected:
            response = None
            logging.warning(self.__class__.__name__, "Not connected!")
            return response
        if not timing:
            response = self.connect.send_command(command)
        else:
            response = self.connect.send_command_timing(command)
        return response
    
    def send_op_command_json(self, cmd, timing=False):
        """
        Send op command with json set and return output in json (dict) format
        """
        if not cmd or (cmd and not isinstance(cmd, str)):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting str received {type(command)}")
        if self.vendor == ('Arista' or 'Cisco'):
            if re.search('([|]+.json$)', cmd):
                command = cmd
            else:
                command = cmd + " | json"
        if not self.is_connected:
            response = None
            logging.warning(self.__class__.__name__, "Not connected!")
            return response
        if not timing:
            response = self.connect.send_command(command)
        else:
            response = self.connect.send_command_timing(command)
        if response and isinstance(response, str):
            response = json.loads(response)
        return response
    
    def disconnect(self):
        """Disconnect from the host device"""
        if not self.is_connected and not self.connected.is_alive():
            logging.warning(self.__class__.__name__, "Not connected!")
        else:
            self.connect.disconnect()
            self.is_connected = False
