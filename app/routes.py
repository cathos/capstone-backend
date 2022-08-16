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
from quart import Blueprint, jsonify, abort, make_response, request
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
async def index():
    '''
    Top-level information
    '''
    return "Running Roaster Control Server version 0.01a"

@roast_bp.route("/init", methods=["POST"])
async def initialize_usb_connection():
    '''
    Negotiate and connect to roaster by usb. Attempt reconnection if necessary. 
    '''
    roaster_dev = await roaster.register_device()
    if roaster_dev is None:
        return await make_response(jsonify("roaster not found"), 500)
    return await make_response(jsonify("connection initialized"), 201)

@roast_bp.route("/release", methods=["POST"])
async def release_usb_connection():
    '''
    Release usb connection so that reconnection can occur. 
    '''
    try: 
        response = await roaster.unregister_device()
        return await make_response(jsonify(response), 201)
    except: 
        return await make_response(jsonify("failed to release connection"), 500)

@roast_bp.route("/info", methods=["GET"])
async def get_roaster_info():
    '''
    send roast info requests over usb and return roaster info
    returns: roaster serial number, firmware version, ... 
    '''
    info_response = await roaster.get_info()
    return await make_response(jsonify(info_response), 200)

@roast_bp.route("/status", methods=["GET"])
async def get_roaster_status():
    '''
    send roast status requests over usb and return roaster status
    returns: bean temperatures, delta temp, roasting state, ...
    '''
    # headers_dict = dict(request.headers)
    # pprint(headers_dict)
    # initial_time = datetime.now()
    status_response = roaster.get_status()
    # response_time_delta = datetime.now() - initial_time
    # print('get roaster status response time', response_time_delta)
    return await make_response(jsonify(status_response), 200)
    

@roast_bp.route("/record", methods=["POST"])
async def record_data(bulkdata_run = False):
    try: 
        recording_state = await request.get_json()["recording_state"]
    except: 
        recording_state = None
    if recording_state == None:
        if bulkdata_run == False:
            return await make_response(jsonify("Not Recording Roast Data"), 200)
        elif bulkdata_run == True:
            return await make_response(jsonify("Recording Roast Data"), 200)
    elif recording_state == "start":
        if bulkdata_run == False:
            bulkdata_run = True
            # background_tasks = set()
            # task = asyncio.create_task(bulk_data_collector())
            # background_tasks.add(task)
            # task.add_done_callback(background_tasks.discard)
            asyncio.run(bulk_data_collector(bulkdata_run))
            return await make_response(jsonify("Data Recording Started"), 201)
        else:
            return await make_response(jsonify("Data Recording Already Running"), 200)
    elif recording_state == "stop":
        bulkdata_run = False
        return await make_response(jsonify("Data Recording Stopped"), 201)


@roast_bp.route("/bulkdata", methods=["GET"])
async def get_bulk_roaster_data():
    '''
    send roast status requests over usb and return last x minutes of roast data
    returns: bean temperatures, delta temp, roasting state, ...
    todo: poll roaster continuously and cache data
    '''
    if bulkdata_run:
        return await make_response(jsonify(list(bulkdata.queue)), 200)
    else: 
        return await make_response(jsonify("Data Collection Not Running"), 400)

@roast_bp.route("/change", methods=["POST"])
async def change_roaster_state():
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
    # print(request.get_json(True))
    request_body = await request.get_json()
    result = request_body['request']
    # request_body = request.get_json()
    print(f"request body {result}")
    if 'PRS' in result:
        roaster.send_command('prs_button')
        status_response = roaster.get_status()
        return make_response(jsonify(status_response['roaster_state']), 201)
    elif 'Heat+' in result:
        status_response = roaster.send_command('heater_increase')
        return make_response(jsonify(status_response['heater_level']), 201)
    elif 'Heat-' in result:
        status_response = roaster.send_command('heater_decrease')
        return make_response(jsonify(status_response['heater_level']), 201)
    elif 'Fan+' in result:
        status_response = roaster.send_command('fan_increase')
        return make_response(jsonify(status_response['fan_level']), 201)
    elif 'Fan-' in result:
        status_response = roaster.send_command('fan_decrease')
        return make_response(jsonify(status_response['fan_level']), 201)
    return make_response(jsonify("command_not_sent"), 400)
