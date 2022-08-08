import json
import os
# from dotenv import load_dotenv
import requests
from flask import Blueprint, jsonify, abort, make_response, request
from app.client.usb_client import Roaster

# load_dotenv()

roast_bp = Blueprint("roast_bp", __name__, url_prefix="")

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
    roaster = Roaster.register_device()
    if roaster is None:
        return make_response(jsonify("roaster not found"), 500)
    return make_response(jsonify("connection initialized"), 201)

@roast_bp.route("/info", methods=["GET"])
def get_roaster_info():
    '''
    send roast info requests over usb and return roaster info
    returns: roaster serial number, firmware version, ... 
    '''
    info_response = Roaster.get_info()
    return make_response(jsonify(info_response), 200)

@roast_bp.route("/status", methods=["GET"])
def get_roaster_status():
    '''
    send roast status requests over usb and return roaster status
    returns: bean temperatures, delta temp, roasting state, ...
    '''
    status_response = Roaster.get_status()
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
        status_response = Roaster.send_command('prs_button')
        return make_response(jsonify(status_response['roaster_state']), 201)
    elif 'Heat+' in request_body:
        status_response = Roaster.send_command('heater_increase')
        return make_response(jsonify(status_response['heater_level']), 201)
    elif 'Heat-' in request_body:
        status_response = Roaster.send_command('heater_decrease')
        return make_response(jsonify(status_response['heater_level']), 201)
    elif 'Fan+' in request_body:
        status_response = Roaster.send_command('fan_increase')
        return make_response(jsonify(status_response['fan_level']), 201)
    elif 'Fan-' in request_body:
        status_response = Roaster.send_command('fan_decrease')
        return make_response(jsonify(status_response['fan_level']), 201)
    return make_response(jsonify("command_not_sent"), 400)
