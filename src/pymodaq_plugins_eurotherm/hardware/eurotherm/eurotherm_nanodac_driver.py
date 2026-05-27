# -*- coding: utf-8 -*-
"""
Python wrapper for Eurotherm 3500 process controllers, with communication via the Modbus RTU protocol.

Highly inspired from minimalmodbus library's example driver for Eurotherm 3500 (eurotherm3500.py file 
originally created by Jonas Berg <pyhys@users.sourceforge.net> in 2012) and adapted for PyMoDAQ software
"""
from tkinter import E
from pymodbus.client import ModbusTcpClient
# from typing import Union#, Tuple
from time import sleep

DEBUG = True

class Nanodac:

    """Instrument class for Nanodac process controller.

    """
    unit:               str = '°C'  # Instrument.Display.Units - Unité d'affichage de l'instrument
    # possibleUnits:      list[str] = ['°C', '°F', 'K','bar'] # Possible units
    AVAILABLE_MEASUREMENT_UNITS:      list[str] = ['°C', '°F', 'K','bar'] # Possible units
    DEFAULT_MEASUREMENT_UNIT= AVAILABLE_MEASUREMENT_UNITS[0]
    # instrumentSerial:   serial.Serial = None
    # slaveAddress:       int = 1     # 0 value is only for slave broadcasting

    # defaults = {
    #     # 'encoding':             'ascii',
    #     'baudrate':             19200,
    #     # 'timeout':              2000,
    #     'parity':               serial.PARITY_NONE,
    #     'bytesize':             8,
    #     'stopbits':             serial.STOPBITS_ONE,
    #     'timeout':              0.05,
    #     'write_timeout':        2.0
    # }

    def __init__(self):
        """
        Args:
            * portname (str): port name
            * slaveaddress (int): slave address in the range 1 to 247
        """
        # minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        # self.instrumentSerial = serial.Serial(
        #     port=None, # Port is set to none to not open port immediately
        #     baudrate=self.defaults['baudrate'],
        #     parity=self.defaults['parity'],
        #     bytesize=self.defaults['bytesize'],
        #     stopbits=self.defaults['stopbits'],
        #     timeout=self.defaults['timeout'],
        #     write_timeout=self.defaults['write_timeout'],
        #     )
        self.ip: str = ip
        # self.instrumentSerial.port = portname # Port is set afterward none to not open port immediately

    def connect(self):
        """Instrument serial port opening
        Returns
        -------
        info: str
        opened: bool
            False if initialization failed otherwise True
        """
        try:
            ModbusTcpClient(ip = self.ip)
            # super().__init__(ip = self.ip)
            # self.instrumentSerial.open() # Already called in parent init

            sleep(0.2) # Make sure connection is established before doing anything else

        except: # serial.SerialException:
            info = f"Failed to open connection at ip : {self.ip}"
            # raise
            pass
        else:
            info =  f"Nanodac connection opened at ip : {self.ip}"

        opened = self.is_socket_open()

        return info, opened

    def get_current_value(self,address):
        """once the instrument is initialized, return its current measured value"""
        value = self.read_holding_registers(address=address, count=1)

        return float(value)

    def set_current_value(self,address,value):
        """once the instrument is initialized, set current  value for consign"""
        self.write_register(address=address, value=value)

        return float(value)


    def disconnect(self):
        self.close()
        return not self.is_socket_open()



    def get_instrument_version(self):
        """Return the instrument version information of the device."""
        return self.read_register(107)

    # def get_instrument_homepage(self):
    #     """Return the instrument homepage of the device."""
    #     return self.read_register(106)

    def get_instrument_type(self):
        """Return a string to precise whether it is a 3508 or 3504 process controller."""
        res = self.read_register(122) # Returns 0 for 3508 device and 1 for 3504 device
        if res == 0:
            return "Eurotherm 3508"
        elif res == 1:
            return "Eurotherm 3504"
        else:
            return "Unknown"

    def get_instrument_display_units(self):
        """"""
        value = self.read_register(516) # Returns 0 if Deg C; 1 if Deg F; 2 if K

        if value == 0:
            self.unit = "°C"
        elif value == 1:
            self.unit =  "°F"
        elif value == 2:
            self.unit =  "K"
        else:
            self.unit =  "unknown unit"

        return self.unit
    
    def set_instrument_display_units(self, unitsStr):
        """Accepted values = {'°C'; '°F'; 'K'}"""

        # Write 0 if Deg C; 1 if Deg F; 2 if K
        if unitsStr == "°C":
            value = 0
        elif unitsStr == "°F":
            value = 1
        elif unitsStr == "K":
            value = 2
        else:
            raise ValueError
        
        self.write_register(516, value, 1)
        self.unit = unitsStr

########################
## Testing the module ##
########################

if __name__ == '__main__':
    print( 'TESTING EUROTHERM 3500 MODBUS MODULE ON COM4 PORT WITH SLAVE ADDRESS 1')

    # serialPort = 'COM4'
    # slaveAddress = 1
    ip='140.77.101.201'
    a = Nanodac(ip)
    a.debug = DEBUG
    info, opened = a.open_communication()

    if opened == False:
        print(f"Failed to open serial port", serialPort, " --> Opening info = ", info)
    else:
        if a.debug == True:
            print(f"Successfully opened serial port ", serialPort, "  --> Opening info = ", info)
        
        # if a.instrumentSerial.is_open:
        print( 'PV:                     {0}'.format(  a.get_pv_loop1()             ))
        print( 'Target SP:              {0}'.format(  a.get_targetSP_loop1()       ))
        print( 'Working SP:             {0}'.format(  a.get_workingSP_loop1()      ))
        print( 'SP-rate Loop1 disabled: {0}'.format(  a.is_sprate_disabled_loop1() ))
        print( 'Output:                 {0} %'.format( a.get_activeOut_loop1()      ))
        print( 'Manual mode Loop1:      {0}'.format(  a.is_manual_loop1()          ))
        print( 'SP rate:                {0}'.format(  a.get_SPrate_loop1()         ))
        print( 'OP rate:                {0} %'.format( a.get_OPrate_loop1()      ))


        print( 'Instrument version:     {0}'.format(  a.get_instrument_version()      ))
        # print( 'Instrument homepage:    {0}'.format(  a.get_instrument_homepage()  ))

        answer = a.get_instrument_type()
        print(f"Connected instruement is an {a.get_instrument_type()}.")

        print(f'Instrument display units:            {a.get_instrument_display_units()}')

        print( 'NANODAC TESTING DONE!' )

# pass

