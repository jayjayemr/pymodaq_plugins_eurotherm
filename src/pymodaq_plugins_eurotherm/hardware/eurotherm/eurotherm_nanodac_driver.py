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

    CHANNELS:dict[str,dict]={'Channel1':{'Main.Descriptor':18688,'Main.PV':256,'Main.Units':18709,'Main.Resolution':6145},
                             'Channel2':{'Main.Descriptor':18715,'Main.PV':260,'Main.Units':18736,'Main.Resolution':6273},
                             'Channel3':{'Main.Descriptor':18742,'Main.PV':264,'Main.Units':18763,'Main.Resolution':6401},
                             'Channel4':{'Main.Descriptor':18769,'Main.PV':268,'Main.Units':18790,'Main.Resolution':6529},
                             'loop1.Main.ActiveOut':{'Main.PV':516},
                             'loop2.Main.ActiveOut':{'Main.PV':654}}

    LOOPS:dict[str,dict]={'Loop1':{'PID.SchedulerType':5685,'Main.PV':512,'Main.TargetSP':514,'Main.AutoMan':513,'Main.ActiveOut':516},
                          'Loop2':{'PID.SchedulerType':5941,'Main.PV':640,'Main.TargetSP':642,'Main.AutoMan':641,'Main.ActiveOut':654}}
    # Loop.2.Main.ActiveOut 644
    # Loop.1.Main.ActiveOut 516

    def __init__(self,ip):
        """
        Args:
            * portname (str): port name
            * slaveaddress (int): slave address in the range 1 to 247
        """
        self.ip = ip
        self.client = ModbusTcpClient(self.ip)

    def connect(self):
        """Instrument serial port opening
        Returns
        -------
        info: str
        opened: bool
            False if initialization failed otherwise True
        """
        try:
            self.client.connect()
            # super().__init__(ip = self.ip)
            info = f"Nanodac connection opened at ip : {self.ip}"
            sleep(0.2) # Make sure connection is established before doing anything else
        except: # serial.SerialException:
            info = f"Failed to open connection at ip : {self.ip}"
        opened = self.client.is_socket_open()
        return opened,info

    def get_current_value(self,address,typeVar='int',count=1):
        """once the instrument is initialized, return its current measured value"""
        try:
            read = self.client.read_holding_registers(address=address, count=count)
        except:
            self.connect()
            self.get_current_value(self, address, typeVar=typeVar, count=count)
        if typeVar =='int':
            returnValue=read.registers[0]
        else:
            returnValue = ''.join(map(chr, list(filter(lambda num: num != 0, read.registers))))
        return returnValue

    def set_current_value(self,address,value):
        """once the instrument is initialized, set current  value for consign"""
        try:
            write=self.client.write_register(address=address, value=value)
        except Exception as e:
            self.connect()
            self.set_current_value(self, address, value)
        return write


    def disconnect(self):
        self.client.close()
        return not self.client.is_socket_open()

#TODO on supprime ?

    # def get_instrument_version(self):
    #     """Return the instrument version information of the device."""
    #     return self.client.read_register(107)
    #
    # # def get_instrument_homepage(self):
    # #     """Return the instrument homepage of the device."""
    # #     return self.read_register(106)
    #
    # def get_instrument_type(self):
    #     """Return a string to precise whether it is a 3508 or 3504 process controller."""
    #     res = self .read_register(122) # Returns 0 for 3508 device and 1 for 3504 device
    #     if res == 0:
    #         return "Nanodac 3508"
    #     elif res == 1:
    #         return "Nanodac 3504"
    #     else:
    #         return "Unknown"
    #
    # def get_instrument_display_units(self):
    #     """"""
    #     value = self.read_register(516) # Returns 0 if Deg C; 1 if Deg F; 2 if K
    #
    #     if value == 0:
    #         self.unit = "°C"
    #     elif value == 1:
    #         self.unit =  "°F"
    #     elif value == 2:
    #         self.unit =  "K"
    #     else:
    #         self.unit =  "unknown unit"
    #
    #     return self.unit
    #
    # def set_instrument_display_units(self, unitsStr):
    #     """Accepted values = {'°C'; '°F'; 'K'}"""
    #
    #     # Write 0 if Deg C; 1 if Deg F; 2 if K
    #     if unitsStr == "°C":
    #         value = 0
    #     elif unitsStr == "°F":
    #         value = 1
    #     elif unitsStr == "K":
    #         value = 2
    #     else:
    #         raise ValueError
    #
    #     self.write_register(516, value, 1)
    #     self.unit = unitsStr

########################
## Testing the module ##
########################

if __name__ == '__main__':
    print( 'TESTING Nanodac MODBUS MODULE PORT WITH SLAVE ADDRESS 1')

    ip='192.168.0.1'
    a = Nanodac(ip)
    a.debug = DEBUG
    info, opened = a.open_communication()

    if opened == False:
        print(f"Nanodac Failed to open serial port",  " --> Opening info = ", info)
    else:
        if a.debug == True:
            print(f"Nanodac Successfully opened serial port ","  --> Opening info = ", info)
        
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

