# coding: utf-8
"""
# check compatibility
import py4web

assert py4web.check_compatible("0.1.20190709.1")

# by importing db you expose it to the _dashboard/dbadmin
from .models import db

# by importing controllers you expose the actions defined in it
from . import controllers

# optional parameters
__version__ = "0.0.0"
__author__ = "you <you@example.com>"
__license__ = "anything you want"
"""
from datetime import datetime
from py4web import action

#from .models import db

#from . import controllers
from .controllers.device_manager import DeviceManager


@action('index')
@action.uses("index.html")
def index():
    return dict(message=f"Hello World @ {datetime.now()}")

@action('devices')
@action.uses("devices.html")
def devices():
    devices = DeviceManager().get_devices()
    return dict(devices=devices)
    #return devices
