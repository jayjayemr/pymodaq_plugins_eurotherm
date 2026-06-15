
from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.utils import ThreadCommand  # object used to send info back to the main thread
from pymodaq_gui.parameter import Parameter

import numpy as np
from pymodaq_plugins_eurotherm.hardware.eurotherm.eurotherm_3500_driver import Eurotherm3500

DEFAULT_COM_PORT = 'COM4'
DEFAULT_SLAVE_ADDRESS = 1

class DAQ_Move_Eurotherm_3500(DAQ_Move_base):
    """ Instrument plugin class for an Eurotherm 3500 process controller.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

    Currently under test on Windows 10 OS, with python=3.11.13 & pymodaq=5.0.18

    /!\ WARNING Current implementation ONLY USES SP1 of PROCESS LOOP NUMBER 1 of the controller 

    Requires minimalmodbus and pyserial to run the hardware driver (Eurotherm3500 class)

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    """
    is_multiaxes = False  # TODO for your plugin set to True if this plugin is controlled for a multiaxis controller
    # _axis_names: Union[List[str], Dict[str, int]] = ['Température', 'Consigne', 'Puissance']  # TODO for your plugin: complete the list
    # _controller_units: Union[str, List[str]] = ['°C', '°C', '%'] # TODO multiaxis support
    _axis_names: Union[List[str], Dict[str, int]] = ['Température']
    _controller_units: Union[str, List[str]] = '°C'
    _epsilon: Union[float, List[float]] = 0.5  # TODO replace this by a value that is correct depending on your controller
    # TODO it could be a single float of a list of float (as much as the number of axes)
    data_actuator_type = DataActuatorType.DataActuator  # wether you use the new data style for actuator otherwise set this
    # as  DataActuatorType.float  (or entirely remove the line)

    params = [  {'title': 'Eurotherm type :', 'name': 'eurotherm_type', 'type': 'str', 'value': 'Unkown', 'readonly': True},
                {'title': 'COM port :', 'name': 'com_port', 'type': 'str', 'value': DEFAULT_COM_PORT, 'readonly': False},
                {'title': 'Modbus slave address :', 'name': 'slaveaddress', 'type': 'int', 'value': DEFAULT_SLAVE_ADDRESS, 'readonly': False},
                {'title': 'Controller units :', 'name': 'controller_units', 'type': 'list', 'value': Eurotherm3500.unit, 'limits': Eurotherm3500.possibleUnits}#,
                ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)
    # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # the target value. It is the developer responsibility to put here a meaningful value

    def ini_attributes(self):
        self.controller: Eurotherm3500 = None

        #TODO declare here attributes you want/need to init with a default value
        pass

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        int or float: The position obtained after scaling conversion.
        """
        pos = DataActuator(data=self.controller.get_pv_loop1(), units=self._controller_units)
        pos = self.get_position_with_scaling(pos)
        return pos

    # def user_condition_to_reach_target(self) -> bool:
    #     """ Implement a condition for exiting the polling mechanism and specifying that the
    #     target value has been reached

    #    Returns
    #     -------
    #     bool: if True, PyMoDAQ considers the target value has been reached
    #     """
    #     # TODO either delete this method if the usual polling is fine with you, but if need you can
    #     #  add here some other condition to be fullfilled either a completely new one or
    #     #  using or/and operations between the epsilon_bool and some other custom booleans
    #     #  for a usage example see DAQ_Move_brushlessMotor from the Thorlabs plugin
    #     return True

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close_communication()

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        # if param.name() == 'axis':
        #     self.axis_unit = self.controller.get_instrument_display_units()
        #     # do this only if you can and if the units are not known beforehand, for instance
        #     # if the motors connected to the controller are of different type (mm, µm, nm, , etc...)
        #     # see BrushlessDCMotor from the thorlabs plugin for an exemple

        if param.name() == "com_port":
            if self.is_master:
                if self.controller.instrumentSerial.is_open:
                    self.controller.close_communication()
                self.controller.instrumentSerial.port = param.value()

        elif param.name() == "slaveaddress":
                self.controller.slaveAddress = param.value()

        elif param.name() == "controller_units":
                self.controller.set_instrument_display_units(param.value())
                self._controller_units = param.value()
                self.axis_unit = param.value()

        else:
            pass

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        if self.is_master:  # is needed when controller is master
            self.controller = Eurotherm3500(portname = self.settings.child('com_port').value(),
                                            slaveaddress=self.settings.child('slaveaddress').value())
            info, initialized = self.controller.open_communication()

        else:
            self.controller = controller
            initialized = True
            info = "Current instrument is a slave, using master controller for operation."

        if initialized:
            tempUnits = self.controller.get_instrument_display_units()
            self.settings.child('controller_units').setValue(tempUnits)
            # self._controller_units = [tempUnits, tempUnits, '%'] # TODO multiaxis support
            self._controller_units = [tempUnits]
            self.axis_unit = [tempUnits]

            self.settings.child('eurotherm_type').setValue(self.controller.get_instrument_type())

            self.controller.set_SPselect_loop1(1) # Use SP1 as current setpoint

        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Set the process controller's (LOOP 1 !) current setpoint to the given value

        Parameters
        ----------
        value: (int or float) value of the absolute target positioning
        """

        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        
        self.controller.set_SP1_loop1(value.value(self.axis_unit))
        self.emit_status(ThreadCommand('Update_Status', [f'Received new setpoint = {value.value(self.axis_unit)}']))

    def move_rel(self, value: DataActuator):
        """ Change the process controller's (LOOP 1 !) current setpoint to the given differential value

        Parameters
        ----------
        value: (int or float) value of the relative target setpoint
        """
        value = self.check_bound(self.current_value + value) - self.current_value
        self.target_value = value + self.current_value
        value = self.set_position_relative_with_scaling(value)

        self.controller.set_SP1_loop1(value.value(self.axis_unit))
        self.emit_status(ThreadCommand('Update_Status', [f'Received new setpoint = {value.value(self.axis_unit)}']))

    def move_home(self):
        """Set the process controller's (LOOP 1 !) current setpoint to zero value of the current unit"""
        zeroValue = DataActuator(   self._title,
                                    data=[np.zeros(self.data_shape, dtype=float)],
                                    units=self.axis_unit)
                                    
        self.controller.set_SP1_loop1(zeroValue.value(self.axis_unit))
        self.emit_status(ThreadCommand('Update_Status', [f'Setpoint reseted to {zeroValue.value(self.axis_unit)}']))

    def stop_motion(self):
        """Stop the process by setting setpoint to actual process value and emits move_done signal"""

        self.target_value = self.current_value
        value = self.set_position_with_scaling(self.current_value)

        self.controller.set_SP1_loop1(value.value(self.axis_unit))
        self.emit_status(ThreadCommand('Update_Status', ['Process has been stopped (setpoint set to current process value).']))


if __name__ == '__main__':
    main(__file__)
