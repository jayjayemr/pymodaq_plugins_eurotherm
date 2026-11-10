import numpy as np
from qtpy import QtWidgets
from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_eurotherm.hardware.eurotherm_nanodac_driver import Nanodac
from pymodaq_plugins_eurotherm.mixin.nanodac_extension import NanodacShowParamMixin

# TODO:
# (1) change the name of the following class to DAQ_0DViewer_TheNameOfYourChoice
# (2) change the name of this file to daq_0Dviewer_TheNameOfYourChoice ("TheNameOfYourChoice" should be the SAME
#     for the class name and the file name.)
# (3) this file should then be put into the right folder, namely IN THE FOLDER OF THE PLUGIN YOU ARE DEVELOPING:
#     pymodaq_plugins_my_plugin/daq_viewer_plugins/plugins_0D

class DAQ_0DViewer_EurothermNanodac(DAQ_Viewer_base, NanodacShowParamMixin):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

        This viewer concerns the eurotherm nanodac recorder/controller
        It has been tested with thermocouple, and pressure sensor
        It has been tested with PyMoDAQ 5.
        Operating system’s version : Ubuntu 24.04
        No manufacturer's driver need to be installed to make it run.

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """
    params = comon_parameters+[
        {'title':'Nanodac IP', 'name': 'Nanodac_IP', 'type': 'str'},
        {'title':'Channel', 'name': 'Channel','type': 'list','limits':list(Nanodac.CHANNELS.keys())},
        {'title': 'Show in LCD', 'name': 'lcd', 'type': 'bool', 'value': False},
        {'title': 'Nanodac Infos', 'name': 'Instrument', 'type': 'action'},
        {'title': 'Channel Infos', 'name': 'Channels', 'type': 'action'},
        {'title': 'DCOutput', 'name': 'DCOutput', 'type': 'action'},
        {'title': 'DigitalIO', 'name': 'DigitalIO', 'type': 'action'},
    ]
    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: Nanodac = None
        self.lcd_init = False
        #TODO declare here attributes you want/need to init with a default value

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings
        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == 'Instrument':
            self.showParam(param.name()) # when writing your own plugin replace this line
        elif param.name() == 'Channels':
            self.showParam(param.name(),self.settings['Channel'])
        elif param.name() == 'DCOutput':
            self.showParam(param.name())
        elif param.name() == 'DigitalIO':
            self.showParam(param.name())
        ##

    def ini_detector(self, controller=None):
        """Detector communication initialization
        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)
        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        ip = self.settings['Nanodac_IP']
        if self.is_master:
            self.controller = Nanodac(self.settings['Nanodac_IP'])  #instantiate you driver with whatever arguments are needed
            initialized, info = self.controller.connect()  # TODO
        else:
            self.controller = controller
            initialized = True

        if 'Main.Units' in self.controller.CHANNELS[self.settings['Channel']].keys():
            unit=self.controller.get_current_value(address=self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],typeVar = 'str', count=6)
            label = self.controller.get_current_value(
                address=self.controller.CHANNELS[self.settings['Channel']]['Main.Descriptor'], typeVar='str', count=21)
            self.dte_signal.emit(DataToExport(name='eurotherm_nanodac',
                                              data=[DataFromPlugins(name=label, data=[np.array([0])],
                                                                    dim='Data0D', labels=[unit])]))
        else:
            #pas d'unité' pour la sortie de W de la boucle donc fixe
            unit="%"
            label = f"Sortie W {self.settings['Channel']}"
        if self.settings['lcd']:
            #pas de nom pour la sortie de W de la boucle donc fixe
            if not self.lcd_init:
                #juste un wiever pas de graph
                self.emit_status(ThreadCommand('init_lcd', dict(labels=[label], Nvals=1, digits=6)))
                QtWidgets.QApplication.processEvents()
                self.lcd_init = True
            self.emit_status(ThreadCommand('lcd', [np.array([0])]))
        info = "detector initialized"
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.disconnect()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector
        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        abs_value = self.controller.get_current_value(address=self.controller.CHANNELS[self.settings['Channel']]['Main.PV'],typeVar='int')
        if 'Main.Units' in self.controller.CHANNELS[self.settings['Channel']].keys():
            res_value=self.controller.get_current_value(address=self.controller.CHANNELS[self.settings['Channel']]['Main.Resolution'])
            label = self.controller.get_current_value(
                address=self.controller.CHANNELS[self.settings['Channel']]['Main.Descriptor'],
                typeVar='str', count=21)
            unit = self.controller.get_current_value(
                address=self.controller.CHANNELS[self.settings['Channel']]['Main.Units'],
                typeVar='str', count=6)
        else:
            res_value=1
            unit = "%"
            label = f"{self.settings['Channel']}"
        value=abs_value/(10**res_value)

        self.dte_signal.emit(DataToExport(name='eurotherm_nanodac',
                                          data=[DataFromPlugins(name=label, data=value,
                                                                dim='Data0D', labels=[unit])]))
        if self.settings['lcd']:
            if not self.lcd_init:
                self.emit_status(ThreadCommand('init_lcd', dict(labels=[label], Nvals=1, digits=6)))
                QtWidgets.QApplication.processEvents()
                self.lcd_init = True
            self.emit_status(ThreadCommand('lcd', [np.array([value])]))



    def stop(self):
        # self.controller.disconnect() # when writing your own plugin remove this line
        self.emit_status(ThreadCommand('Update_Status', ['stop nanodac acquisition']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)
