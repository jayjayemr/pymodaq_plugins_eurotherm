from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.utils import ThreadCommand  # object used to send info back to the main thread
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_eurotherm.hardware.eurotherm_nanodac_driver import Nanodac
from pymodaq_plugins_eurotherm.mixin.nanodac_extension import NanodacShowParamMixin

class DAQ_Move_EurothermNanodac(DAQ_Move_base, NanodacShowParamMixin):
    """ Instrument plugin class for an Eurotherm NanoDac process controller.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.



    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    """
    is_multiaxes = True  # TODO for your plugin set to True if this plugin is controlled for a multiaxis controller
    _axis_names: Union[List[str], Dict[str, int]] = ['Température', 'Consigne', 'Puissance']  # TODO for your plugin: complete the list
    # _controller_units: Union[str, List[str]] = ['°C', '°C', '%'] # TODO multiaxis support
    # _axis_names: Union[List[str], Dict[str, int]] = ['Température']
    _controller_units: Union[str, List[str]] = ['°C','%','bar']
    _epsilons: Union[float, List[float]] = 0.5  # TODO replace this by a value that is correct depending on your controller
    # TODO it could be a single float of a list of float (as much as the number of axes)
    data_actuator_type = DataActuatorType.DataActuator  # wether you use the new data style for actuator otherwise set this
    # as  DataActuatorType.float  (or entirely remove the line)

    params = [  {'title': 'Nanodac IP', 'name': 'Nanodac_IP', 'type': 'str'},
                {'title': 'Loop', 'name': 'Loop', 'type': 'list', 'limits': list(Nanodac.LOOPS.keys())},
                {'title': 'Channel', 'name': 'Channel', 'type': 'list', 'limits': list(Nanodac.CHANNELS.keys())},
                {'title': 'Nanodac Infos', 'name': 'Instrument', 'type': 'action'},
                {'title': 'Loop Infos', 'name': 'Loops', 'type': 'action'},
                {'title': 'I/O Infos', 'name': 'IORead', 'type': 'action'},
                ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilons)
    # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # the target value. It is the developer responsibility to put here a meaningful value

    def ini_attributes(self):
        self.controller: Nanodac = None

        #TODO declare here attributes you want/need to init with a default value
        pass

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        int or float: The position obtained after scaling conversion.
        """
        res_value=0
        value=self.controller.get_current_value(self.controller.LOOPS[self.settings['Loop']]['Main.PV'], typeVar='int')
        if 'Main.Resolution' in self.controller.CHANNELS[self.settings['Channel']]:
            res_value = self.controller.get_current_value(
                address=self.controller.CHANNELS[self.settings['Channel']]['Main.Resolution'], typeVar='int')
        value = value / (10 ** res_value)
        if 'Main.Units' in self.controller.CHANNELS[self.settings['Channel']]:
            unit = self.controller.get_current_value(self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],typeVar='str', count=6)
            # pos = DataActuator(data=value,units=unit)
            pos = DataActuator(data=value,units=self._controller_units)
        else:
            # pos = DataActuator(data=value)
            pos = DataActuator(data=value,units=self._controller_units)
        pos = self.get_position_with_scaling(pos)
        # #TODO  units ??
        # # print(self.controller.CHANNELS[self.settings['Channel']]['Main.Units'])
        # # print(self.controller.get_current_value(self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],typeVar='str', count=6))
        # # print(f"  {self.settings['Loop']} {self.settings['Channel']} {self.controller.get_current_value(self.controller.LOOPS[self.settings['Loop']]['Main.PV'])} => {self.controller.get_current_value(self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],typeVar='str', count=6)}")
        # pos = DataActuator(data=value,
        #                    units=self.controller.get_current_value(self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],typeVar='str', count=6))
        # pos = self.get_position_with_scaling(pos)
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
            self.controller.disconnect()

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'Instrument':
            self.showParam(param.name())  # when writing your own plugin replace this line
        elif param.name() == 'Loops':
            self.showParam(param.name(),self.controller.LOOPS)
        elif param.name() == 'IORead':
            self.showParam(param.name())

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
            self.controller = Nanodac(self.settings['Nanodac_IP'])
            initialized, info = self.controller.connect()

        else:
            self.controller = controller
            initialized = True
            info = "Current instrument is a slave, using master controller for operation."

        if initialized:
            if 'Main.Units' in self.controller.CHANNELS[self.settings['Channel']]:
                self._controller_units = self.controller.get_current_value(address=self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],
                                                     typeVar='str', count=6)
                self.axis_unit = self.controller.get_current_value(address=self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],
                                                     typeVar='str', count=6)
            else:
                self._controller_units="%"
                # self.axis_unit=["%"]
                self.axis_unit="%"
        return info, initialized

    def move_abs(self, value: DataActuator):
        value = self.check_bound(value)
        self.target_value = value
        value = value.value()  # ← float pur, sans unité Pint
        res_value = self.controller.get_current_value(
            address=self.controller.CHANNELS[self.settings['Channel']]['Main.Resolution'],
            typeVar='int')
        value = int(value * (10 ** res_value))
        self.controller.set_current_value(
            self.controller.LOOPS[self.settings['Loop']]['Main.TargetSP'], value)
        self.controller.set_current_value(
            self.controller.LOOPS[self.settings['Loop']]['Main.AutoMan'], 0)
        self.emit_status(ThreadCommand('Update_Status',
                                       [f'Received new setpoint = {self.target_value} {self.axis_unit}']))

    def move_rel(self, value: DataActuator):
        value = self.check_bound(self.current_value + value) - self.current_value
        self.target_value = self.current_value + value  # DataActuator en °C, avant extraction
        delta = value.value()  # ← float pur (delta en °C)
        res_value = 0
        if 'Main.Resolution' in self.controller.CHANNELS[self.settings['Channel']]:
            res_value = self.controller.get_current_value(
                address=self.controller.CHANNELS[self.settings['Channel']]['Main.Resolution'], typeVar='int')
        target = self.current_value.value() + delta  # consigne absolue en °C
        value = int(target * (10 ** res_value))  # conversion en unités brutes
        self.controller.set_current_value(
            self.controller.LOOPS[self.settings['Loop']]['Main.TargetSP'], value)
        self.controller.set_current_value(
            self.controller.LOOPS[self.settings['Loop']]['Main.AutoMan'], 0)
        self.emit_status(ThreadCommand('Update_Status',
                                       [f'Received new setpoint = {self.target_value} {self.axis_unit}']))

    def move_home(self):
        self.controller.set_current_value(
            self.controller.LOOPS[self.settings['Loop']]['Main.TargetSP'], 0)
        self.emit_status(ThreadCommand('Update_Status', ['Setpoint reset to 0']))

    def stop_motion(self):
        """Stop the process by setting setpoint to actual process value and emits move_done signal"""
        self.controller.set_current_value(self.controller.LOOPS[self.settings['Loop']]['Main.AutoMan'], 1)
        self.emit_status(ThreadCommand('Update_Status', ['Process has been stopped (setpoint set to current process value).']))


if __name__ == '__main__':
    main(__file__)
