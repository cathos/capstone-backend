import json
import os
from dotenv import load_dotenv
import requests
from flask import Blueprint, jsonify, abort, make_response, request


load_dotenv()

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
    return make_response(jsonify("connection initialized"), 201)

@roast_bp.route("/info", methods=["GET"])
def get_roaster_info():
    '''
    send roast info requests over usb and return roaster info
    returns: roaster serial number, firmware version, ... 
    '''
    return make_response(jsonify("info_response"), 200)

@roast_bp.route("/status", methods=["GET"])
def get_roaster_status():
    '''
    send roast status requests over usb and return roaster status
    returns: bean temperatures, delta temp, roasting state, ...
    '''
    return make_response(jsonify("status_response"), 200)

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
        #send PRS command
        return make_response(jsonify("sent_command"), 201)
    return make_response(jsonify("command_not_sent"), 400)
