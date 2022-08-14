import asyncio
from asyncio import streams
from datetime import datetime
import json
import os
from pprint import pprint
from queue import Queue
import time
# from dotenv import load_dotenv
import requests
from flask import Blueprint, jsonify, abort, make_response, request
# from app.client.roaster_const import AILLIO
from app.client.usb_client import Roaster

# load_dotenv()

roast_bp = Blueprint("roast_bp", __name__, url_prefix="")
roaster = Roaster()
bulkdata = Queue(maxsize=3600)
bulkdata_run = False
roaster_dev = roaster.register_device()

async def bulk_data_runner():
    '''
    async function to continuously get & cache roaster data
    '''
    status_response = roaster.get_status()
    time.sleep(0.5)
    bulkdata.put(status_response)
    # return bulkdata
    

async def bulk_data_collector(bulkdata_run):
    '''
    collector for bulk_data_runner
    '''
    response = None
    while bulkdata_run: 
        response = await bulk_data_runner()
        time.sleep(0)
    
    # return "last response: ", response, "bulkdata_run: ", bulkdata_run, "bulkdata collection stopped", list(bulkdata.queue)
        

@roast_bp.route("/", methods=["GET"])
def index():
    '''
    Top-level information
    '''
    return "Running Roaster Control Server version 0.01a"

@roast_bp.route("/init", methods=["POST"])
def initialize_usb_connection():
    '''
    Negotiate and connect to roaster by usb. Attempt reconnection if necessary. 
    '''
    roaster_dev = roaster.register_device()
    if roaster_dev is None:
        return make_response(jsonify("roaster not found"), 500)
    return make_response(jsonify("connection initialized"), 201)

@roast_bp.route("/release", methods=["POST"])
def release_usb_connection():
    '''
    Release usb connection so that reconnection can occur. 
    '''
    try: 
        response = roaster.unregister_device()
        return make_response(jsonify(response), 201)
    except: 
        return make_response(jsonify("failed to release connection"), 500)

@roast_bp.route("/info", methods=["GET"])
def get_roaster_info():
    '''
    send roast info requests over usb and return roaster info
    returns: roaster serial number, firmware version, ... 
    '''
    info_response = roaster.get_info()
    return make_response(jsonify(info_response), 200)

@roast_bp.route("/status", methods=["GET"])
def get_roaster_status():
    '''
    send roast status requests over usb and return roaster status
    returns: bean temperatures, delta temp, roasting state, ...
    '''
    headers_dict = dict(request.headers)
    pprint(headers_dict)
    initial_time = datetime.now()
    status_response = roaster.get_status()
    response_time_delta = datetime.now() - initial_time
    print('get roaster status response time', response_time_delta)
    return make_response(jsonify(status_response), 200)

@roast_bp.route("/startbulkrecording", methods=["POST"])
def start_bulk_recording():
    bulkdata_run = True
    # background_tasks = set()
    # task = asyncio.create_task(bulk_data_collector())
    # background_tasks.add(task)
    # task.add_done_callback(background_tasks.discard)
    asyncio.run(bulk_data_collector(bulkdata_run))
    return make_response(jsonify("Bulk Data Recording Started"), 201)

@roast_bp.route("/bulkdata", methods=["GET"])
def get_bulk_roaster_data():
    '''
    send roast status requests over usb and return last x minutes of roast data
    returns: bean temperatures, delta temp, roasting state, ...
    todo: poll roaster continuously and cache data
    '''
    print(f"bulkdata_run: {bulkdata_run}")
    print(list(bulkdata.queue))   
    return make_response(jsonify(list(bulkdata.queue)), 200)

@roast_bp.route("/change", methods=["POST"])
def change_roaster_state():
    '''
    act on the following 'buttons':
    - PRS (change roaster modes - Preheat, (Charge), Roast, Cooling, Shutdown, Off)
    - Heat+ & -
    - Fan+ & -
    Add these later:
    - Drum+ & -
    - Cooling Fan+ & -
    - other?
    Maybe use try-except with the usb errors?
    '''
    print(request.get_json(True))
    request_body = request.get_json()['request']
    print(f"request_body {request_body}")
    if 'PRS' in request_body:
        roaster.send_command('prs_button')
        status_response = roaster.get_status()
        return make_response(jsonify(status_response['roaster_state']), 201)
    elif 'Heat+' in request_body:
        status_response = roaster.send_command('heater_increase')
        return make_response(jsonify(status_response['heater_level']), 201)
    elif 'Heat-' in request_body:
        status_response = roaster.send_command('heater_decrease')
        return make_response(jsonify(status_response['heater_level']), 201)
    elif 'Fan+' in request_body:
        status_response = roaster.send_command('fan_increase')
        return make_response(jsonify(status_response['fan_level']), 201)
    elif 'Fan-' in request_body:
        status_response = roaster.send_command('fan_decrease')
        return make_response(jsonify(status_response['fan_level']), 201)
    return make_response(jsonify("command_not_sent"), 400)
