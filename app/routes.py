from datetime import datetime
import json
import os
# from dotenv import load_dotenv
import requests
from flask import Blueprint, jsonify, abort, make_response, request
# from app.client.roaster_const import AILLIO
from app.client.usb_client import Roaster

# load_dotenv()

roast_bp = Blueprint("roast_bp", __name__, url_prefix="")
roaster = Roaster()

roaster_dev = roaster.register_device()

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
    initial_time = datetime.now()
    status_response = roaster.get_status()
    response_time_delta = datetime.now() - initial_time
    print('get roaster status response time', response_time_delta)
    return make_response(jsonify(status_response), 200)

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
    request_body = request.get_json()
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
