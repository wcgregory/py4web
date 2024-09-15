# coding: utf-8 #

import logging
import os
import re
import json

from netmiko import NetmikoTimeoutException
from paramiko.ssh_exception import AuthenticationException, SSHException
from netmiko.ssh_dispatcher import ConnectHandler

USER = 'admin'
PSWD = 'C1sco12345'
#PSWD = os.getenv('PSWD')


class NetConnect():
    """
    Netmiko ConnectHandler wrapper class
    """
    def __init__(self, host=None, vendor=None):
        self.host = host
        self.host_vendor = vendor
        self.host_os = None
        self.username = None
        self.password = None
        self.connect = None
        self.is_connected = False
        if self.host_vendor:
            self.device_type = self.set_netmiko_device_type(vendor=self.host_vendor)
    
    def set_username(self, username):
        self.username = username
    
    def set_password(self, password):
        self.password = password

    def set_host_os(self, os):
        self.host_os = os
    
    def set_netmiko_device_type(self, vendor=None):
        """Set netmiko device_type based on vendor"""
        if not vendor and not self.host_vendor:
            raise ValueError(self.__class__.__name__, "Invalid or missing vendor of host")
        else:
            self.host_vendor = vendor.strip().capitalize()
        if self.host_vendor == 'Arista':
            self.device_type = 'arista_eos'
        elif self.host_vendor == 'Cisco':
            if self.host_os and self.host_os == 'nxos':
                self.device_type = 'cisco_nxos_ssh'
            else:
                self.device_type = 'cisco_ios'
        elif self.host_vendor == 'Juniper':
            self.device_type = 'juniper_junos'
        else:
            self.device_type = 'unknown'
    
    def connect_to_device(self, auth=None):
        """Connect to the host device"""
        if self.is_connected:
            logging.warning(f"{self.__class__.__name__}, Already connected")
            return False
        if not self.username and not isinstance(auth, tuple):
            logging.warning(f"{self.__class__.__name__}, No login credentials set")
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
            logging.warning(f"{self.__class__.__name__}, No response, connection timed out!")
        except (AuthenticationException):
            logging.warning(f"{self.__class__.__name__}, No login credentials set!")
        except (SSHException):
            logging.warning(f"{self.__class__.__name__}, SSH issue!")
        except Exception as unknown_error:
            logging.warning(f"{self.__class__.__name__}, Unexpected error!")
        if self.connect and self.connect.is_alive():
            self.is_connected = True

    def send_op_command(self, cmd, timing=False, use_textfsm=False):
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
            if not use_textfsm:
                response = self.connect.send_command(command)
            else:
                response = self.connect.send_command(command, use_textfsm=True)
        elif timing and use_textfsm:
            response = self.connect.send_command_timing(command, use_textfsm=True)
        else:
            response = self.connect.send_command_timing(command)
        return response
    
    def send_op_command_json(self, cmd, timing=False):
        """
        Send op command with json set and return output in json (dict) format
        """
        if self.host_vendor == 'Arista' or self.host_vendor == 'Cisco':
            if re.search('([|]+.json$)', cmd):
                command = cmd
            else:
                command = cmd + " | json"
        if not command or (command and not isinstance(command, str)):
            raise TypeError(self.__class__.__name__, f"Invalid type expecting str received {type(command)}")
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
