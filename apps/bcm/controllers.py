# coding: utf-8

import os
from datetime import datetime

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import (
    db, session, T, cache, auth, logger,
    authenticated, unauthenticated, flash
)
from .modules.device_manager import DeviceManager
from .modules.result_reviewer import ResultsReview
from .modules.network_poller import NetworkPoller

@action('index')
@action.uses("index.html")
def index():
    return dict(message=f"Hello World @ {datetime.now()}")

@action("devices")
@action.uses("devices.html")
def devices():
    devices = DeviceManager().get_devices()
    return dict(devices=devices)

@action("devices/<device_id:int>")
@action.uses("device.html")
def device(device_id):
    device = DeviceManager().get_devices(device=device_id)[0]
    last_res = list(device['results'])
    last_res.sort()
    device.update({"last_result": device['results'][last_res[-1]]})
    url=URL("run_commands")
    return dict(device=device, url=url)

@action("devices/<device_id:int>/results")
@action.uses("device_results.html")
def device_results(device_id):
    results = ResultsReview().get_results(device=device_id)
    results_list = [results[device_id][result] for result in results[device_id]]
    return dict(results=results_list)

@action('results')
@action.uses("results.html")
def results():
    results = ResultsReview().get_results()
    return dict(results=results)

@action("run_commands/<device_id:int>", method=["GET"])
def run_commands(device_id):
    """
    export USERACC='admin'
    export IOSPASS='C1sco12345'
    export NXOSPASS='Admin_1234'
    """
    if device_id == 3:
        user_creds = (os.getenv('USERACC'), os.getenv('IOSPASS'))
    if device_id == 4:
        user_creds = (os.getenv('USERACC'), os.getenv('NXOSPASS'))
    device = NetworkPoller(device_id=device_id)
    device.load_device_commands()
    device.run_device_commands(auth=user_creds)
    device.save_results()
    return dict()

@action("roles/<device_roles>")
@action.uses("devices_by_role.html")
def devices_by_role(device_roles):
    devices = DeviceManager().get_devices(roles=device_roles)
    return dict(role=device_roles, devices=devices)
