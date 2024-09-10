"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from datetime import datetime

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import (db, session, T, cache, auth, logger, authenticated, unauthenticated, flash,)
from .modules.device_manager import DeviceManager
from .modules.result_reviewer import ResultsReview

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
def devices(device_id):
    device = DeviceManager().get_devices(device=device_id)[0]
    last_res = list(device['results'])
    last_res.sort()
    device.update({"last_result": device['results'][last_res[-1]]})
    return dict(device=device)

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
