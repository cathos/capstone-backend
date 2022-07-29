# ctrl_transfer( bmRequestType, bmRequest, wValue, wIndex, nBytes)

from struct import unpack
import usb.core
import usb.util
# import usb.control
import sys
 
Aillio = {
    'vendor':0x483,
    'product':0xa27e,
    'configuration':0x1,
    'interface':0x1,
    'debug':0x1,
    'write_endpoint':0x3,
    'read_endpoint':0x81,
    'commands':{
        'info_1':[0x30, 0x02],
        'info_2':[0x89, 0x01],
        'status_1': [0x30, 0x01],
        'status_2': [0x30, 0x03],
        'prs_button': [0x30, 0x01, 0x00, 0x00],
        'heater_increase': [0x34, 0x01, 0xaa, 0xaa],
        'heater_decrease': [0x34, 0x02, 0xaa, 0xaa],
        'fan_increase': [0x31, 0x01, 0xaa, 0xaa],
        'fan_decrease': [0x31, 0x02, 0xaa, 0xaa],
    },
    'state':{
        'off': 0x00,
        'preheating': 0x02,
        'charge': 0x04,
        'roasting': 0x06,
        'cooling': 0x08,
        'shutdown': 0x09,
    },
}

# def register_device(): 
dev = usb.core.find(idVendor=Aillio['vendor'], idProduct=0xa27e)
if dev is None:
    raise ValueError('Device not found')
    # return dev

 
# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration(configuration=0x1)
 
usb.util.claim_interface(dev, 0x1)

def send(command):
    dev.write(Aillio['write_endpoint'], command)

def receive(length=32):
    '''
    length is either 32 or 64 (or maybe 36?)
    '''
    received_data = dev.read(Aillio['read_endpoint'], length)

    return received_data

def convert_data(received_data, data_type):
    if data_type == 'serial_number':
        converted = unpack('h', received_data[0:2])[0]
    elif data_type == 'firmware':
        converted = unpack('h', received_data[24:26])[0]
    elif data_type == 'batches':
        converted = unpack('>I', received_data[27:31])[0]
    elif data_type == 'bean_temp':
        converted = round(unpack('f', received_data[0:4])[0], 1)
    elif data_type == 'roaster_status':
        converted = {
            'bean_temp': round(unpack('f', received_data[0:4])[0], 1),
        }
    return converted

send(Aillio['commands']['info_1'])
reply = receive()
print(convert_data(reply, 'serial_number'))
print(convert_data(reply, 'firmware'))

send(Aillio['commands']['info_2'])
reply = receive(36)
print(convert_data(reply, 'batches'))

send(Aillio['commands']['status_1'])
reply1 = receive(64)
send(Aillio['commands']['status_2'])
reply2 = receive(64)
reply = reply1 + reply2 

print(convert_data(reply, 'roaster_status'))

# # Let's fuzz around! 
 
# # Lets start by Reading 1 byte from the Device using different Requests
# # bRequest is a byte so there are 255 different values
# for bRequest in range(255):
#     try:
#         ret = dev.ctrl_transfer(0xC0, bRequest, 0, 0, 1)
#         print ("bRequest ",bRequest)
#         print (ret)
#     except:
#         # failed to get data for this request
#         pass

# cfg = dev.get_active_configuration()
# intf = cfg[(0,0)]

# ep = usb.util.find_descriptor(
#     intf,
#     # match the first OUT endpoint
#     custom_match = \
#     lambda e: \
#         usb.util.endpoint_direction(e.bEndpointAddress) == \
#         usb.util.ENDPOINT_OUT)

# assert ep is not None

# # write the data
# ep.write('test')