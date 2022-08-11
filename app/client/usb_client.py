# ctrl_transfer( bmRequestType, bmRequest, wValue, wIndex, nBytes)
from pprint import pprint
import struct
from struct import *
from .roaster_const import AILLIO
import usb.core
import usb.util
# import usb.control
import sys

class Roaster:
    def __init__(self):
        self.dev = None
        self.info = ""
        self.status = ""

    def register_device(self): 
        self.dev = usb.core.find(idVendor=AILLIO['vendor'], idProduct=AILLIO['product'])

        try:
            active_config = self.dev.get_active_configuration()
        except usb.core.USBError:
            active_config = None
        if active_config is None or active_config.bConfigurationValue != 0x1:
            self.dev.set_configuration(configuration=0x1)

        if self.dev is None:
            raise ValueError('Device not found')

        # detach roaster if it is currently held by another process (from https://github.com/pyusb/pyusb/issues/76#issuecomment-118460796)
        # # there is probably a cleaner way to do this, and this seems to fail occasionally. 
        # for cfg in self.dev:
        #     for intf in cfg:
        #         if self.dev.is_kernel_driver_active(intf.bInterfaceNumber):
        #             try:
        #                 self.dev.detach_kernel_driver(intf.bInterfaceNumber)
        #             except usb.core.USBError as e:
        #                 sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))
        
        usb.util.claim_interface(self.dev, 0x1)

        return self.dev
    
    def unregister_device(self):
        self.dev = usb.core.find(idVendor=AILLIO['vendor'], idProduct=AILLIO['product'])
        for cfg in self.dev:
            for intf in cfg:
                if self.dev.is_kernel_driver_active(intf.bInterfaceNumber):
                    try:
                        self.dev.detach_kernel_driver(intf.bInterfaceNumber)
                    except usb.core.USBError as e:
                        sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))
        
        # self.dev.detach_kernel_driver()
        usb.util.release_interface(self.dev, 0x1)
        return 

    @staticmethod
    def convert_data(received_data, data_type):
        '''
        Aillio-specific logic to convert the return data from a C struct into python data types
        - possibly refactor into a generic function and move specific logic into its own class later.
        '''
        if data_type == 'info': 
            converted = {
                'serial_number': unpack('h', received_data[0:2])[0],
                'firmware': unpack('h', received_data[24:26])[0],
                'batches': unpack('>I', received_data[59:63])[0],
            }
        elif data_type == 'status':
            converted = {
                'bean_temp': round(unpack('f', received_data[0:4])[0], 1),
                'bt_ror': round(unpack('f', received_data[4:8])[0], 1),
                'delta_t': round(unpack('f', received_data[8:12])[0], 1),
                'ext_t': round(unpack('f', received_data[16:20])[0], 1),
                'roast_minutes': received_data[24],
                'roast_seconds': received_data[25],
                'fan_level': received_data[26],
                'heater_level': received_data[27],
                'drum_speed_level': received_data[28],
                'roaster_state': AILLIO['state'][received_data[29]],
                'ir_bt': round(unpack('f', received_data[32:36])[0], 1),
                'pcb_temp': round(unpack('f', received_data[36:40])[0], 1),
                'fan_speed': unpack('h', received_data[44:46])[0],
                'voltage': unpack('h', received_data[48:50])[0],
                'coil_fan_1_rpm': round(unpack('i', received_data[52:56])[0], 1),
                'coil_fan_2_rpm': round(unpack('i', received_data[96:100])[0], 1),
                'preheat_temp': unpack('h', received_data[40:42])[0],
            }
        return converted

    def send(self, command):
        '''
        possibly refactor the send-recieve loop into an async function in the future?
        '''
        self.dev.write(AILLIO['write_endpoint'], command)

    def receive(self, length=32):
        '''
        length is 32, 36, or 64
        '''
        received_data = self.dev.read(AILLIO['read_endpoint'], length)

        return received_data
    
    def get_info(self):
        self.send(AILLIO['commands']['info_1'])
        info_1 = self.receive()
        self.send(AILLIO['commands']['info_2'])
        info_2 = self.receive(36)
        recieved_data = info_1 + info_2
        self.info = self.convert_data(recieved_data, 'info')
        return self.info

    def get_status(self):
        self.send(AILLIO['commands']['status_1'])
        status_1 = self.receive(64)
        self.send(AILLIO['commands']['status_2'])
        status_2 = self.receive(64)
        recieved_data = status_1 + status_2
        self.status = self.convert_data(recieved_data, 'status')
        return self.status

    def send_command(self, command):
        try: 
            self.send(AILLIO['commands'][command])
            roaster_status = self.get_status()
            return roaster_status
        except: 
            return 'invalid command'

    def print_all(self):
        pprint(f'info:{self.info}')
        pprint(f'status:{self.status}')
        pass