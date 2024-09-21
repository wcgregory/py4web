# coding: utf-8

import os
from datetime import datetime

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import (
    db, session, T, cache, auth, logger,
    authenticated, unauthenticated, flash
)
from .models import DEVICE_ROLES
from .modules.device_manager import DeviceManager
from .modules.result_reviewer import ResultsReview
from .modules.network_poller import NetworkPoller

@action('index')
@action.uses("index.html")
def index():
    return dict(
        message=f"{datetime.now()}",
        #devices_url=URL('get_devices')
    )

@action("devices")
@action.uses("devices.html")
def devices():
    devices = DeviceManager().get_devices(max_results=10)
    return dict(devices=devices)

@action('results')
@action.uses("results.html")
def results():
    results = ResultsReview().get_results()
    return dict(results=results)

@action("get_devices")
def get_devices():
    devices = DeviceManager().get_devices()
    return dict(devices=devices)

@action("selected_device/<device_id:int>")
def selected_device(device_id):
    device = DeviceManager().get_devices(device=device_id)
    return dict(device=device)

@action("get_device_roles")
def get_device_roles():
    return dict(roles=DEVICE_ROLES)

#@action("get_devices_by_role/:device_role")
#def get_devices_by_role(device_role):
#    devices = DeviceManager().get_devices(roles=device_role)
#    return dict(devices_by_role=devices)

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
def device_results(device_id, limit=None):
    results = ResultsReview().get_results(device=device_id)
    results_list = [results[device_id][result] for result in results[device_id]]
    return dict(device_id=device_id, partial=limit, results=results_list)

@action("devices/<device_id:int>/partialresults")
@action.uses("device_results.html")
def device_results(device_id, limit=10):
    results = ResultsReview().get_results(device=device_id)
    results_list = [results[device_id][result] for result in results[device_id]]
    if limit and limit >= len(results):
        results_list = results_list[-limit:]
    return dict(device_id=device_id, partial=limit, results=results_list)

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

@action("run_commands_by_role/<device_role>", method=["GET"])
def run_commands_by_role(device_role):
    devices = DeviceManager().get_devices(roles=device_role)
    for device in devices:
        if device['id'] == 3:
            user_creds = (os.getenv('USERACC'), os.getenv('IOSPASS'))
        #if device['id'] == 4:
        #    user_creds = (os.getenv('USERACC'), os.getenv('NXOSPASS'))
        else:
            continue
        device = NetworkPoller(device_id=device['id'])
        device.load_device_commands()
        device.run_device_commands(auth=user_creds)
        device.save_results()
    redirect(URL(f"roles/{device_role}"))
    return dict()

@action("roles/<device_role>")
@action.uses("devices_by_role.html")
def devices_by_role(device_role):
    devices = DeviceManager().get_devices(roles=device_role, max_results=10)
    url=URL("run_commands_by_role")
    return dict(dev_role=device_role, devices=devices, url=url)
