# ctrl_transfer( bmRequestType, bmRequest, wValue, wIndex, nBytes)

from struct import Struct, unpack
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

# detach roaster if it is currently held by another process (from https://github.com/pyusb/pyusb/issues/76#issuecomment-118460796)
for cfg in dev:
  for intf in cfg:
    if dev.is_kernel_driver_active(intf.bInterfaceNumber):
      try:
        dev.detach_kernel_driver(intf.bInterfaceNumber)
      except usb.core.USBError as e:
        sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))
 
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

convert_struct = Struct(format='f')

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
            'bean_temp': round(convert_struct.unpack(received_data[0:4])[0], 1),
            'fan_speed': convert_struct.unpack('h', received_data[44:46])[0],
            'ir_temp': round(convert_struct.unpack(received_data[32:36])[0], 1),
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

print(f"Reply1: {reply1}")
print(f"Reply2: {reply2}")
print(f"Convert Reply1: {convert_struct.iter_unpack(reply1)}")
print(f"Convert Reply2: {convert_struct.iter_unpack(reply2)}")



print(convert_data(reply, 'roaster_status'))


# # Stuff from Artisan's Aillio config file:
# valid = state[41]
#         # Heuristic to find out if the data is valid
#         # It looks like we get a different message every 15 seconds
#         # when we're not roasting.  Ignore this message for now.
#         if valid == 10:
#             self.bt = round(unpack('f', state[0:4])[0], 1)
#             self.bt_ror = round(unpack('f', state[4:8])[0], 1)
#             self.dt = round(unpack('f', state[8:12])[0], 1)
#             self.exitt = round(unpack('f', state[16:20])[0], 1)
#             self.minutes = state[24]
#             self.seconds = state[25]
#             self.fan = state[26]
#             self.heater = state[27]
#             self.drum = state[28]
#             self.r1state = state[29]
#             self.irt = round(unpack('f', state[32:36])[0], 1)
#             self.pcbt = round(unpack('f', state[36:40])[0], 1)
#             self.fan_rpm = unpack('h', state[44:46])[0]
#             self.voltage = unpack('h', state[48:50])[0]
#             self.coil_fan = round(unpack('i', state[52:56])[0], 1)
#             self.__dbg('BT: ' + str(self.bt))
#             self.__dbg('BT RoR: ' + str(self.bt_ror))
#             self.__dbg('DT: ' + str(self.dt))
#             self.__dbg('exit temperature ' + str(self.exitt))
#             self.__dbg('PCB temperature: ' + str(self.irt))
#             self.__dbg('IR temperature: ' + str(self.pcbt))
#             self.__dbg('voltage: ' + str(self.voltage))
#             self.__dbg('coil fan: ' + str(self.coil_fan))
#             self.__dbg('fan: ' + str(self.fan))
#             self.__dbg('heater: ' + str(self.heater))
#             self.__dbg('drum speed: ' + str(self.drum))
#             self.__dbg('time: ' + str(self.minutes) + ':' + str(self.seconds))

#         state = state[64:]
#         self.coil_fan2 = round(unpack('i', state[32:36])[0], 1)
#         self.pht = unpack('H', state[40:42])[0]
#         self.__dbg('pre-heat temperature: ' + str(self.pht))
#         if self.r1state == self.AILLIO_STATE_OFF:
#             self.state_str = 'off'
#         elif self.r1state == self.AILLIO_STATE_PH:
#             self.state_str = 'pre-heating to ' + str(self.pht) + 'C'
#         elif self.r1state == self.AILLIO_STATE_CHARGE:
#             self.state_str = 'charge'
#         elif self.r1state == self.AILLIO_STATE_ROASTING:
#             self.state_str = 'roasting'
#         elif self.r1state == self.AILLIO_STATE_COOLING:
#             self.state_str = 'cooling'
#         elif self.r1state == self.AILLIO_STATE_SHUTDOWN:
#             self.state_str = 'shutdown'
#         self.__dbg('state: ' + self.state_str)
#         self.__dbg('second coil fan: ' + str(self.coil_fan2))

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