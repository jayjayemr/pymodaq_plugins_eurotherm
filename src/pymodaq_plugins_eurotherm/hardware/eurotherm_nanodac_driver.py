# -*- coding: utf-8 -*-
"""
Python wrapper for Eurotherm Nanodac process controllers, with communication via the Modbus RTU protocol.

"""
# from tkinter import E
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# from typing import Union#, Tuple
from time import sleep

DEBUG = True

class Nanodac:

    """Instrument class for Nanodac process controller.

    """
    unit:               list[str] = ['°C','%','bar'] # Instrument.Display.Units - Unité d'affichage de l'instrument
    # possibleUnits:      list[str] = ['°C', '°F', 'K','bar'] # Possible units
    AVAILABLE_MEASUREMENT_UNITS:      list[str] = ['°C', '°F', 'K','bar'] # Possible units
    DEFAULT_MEASUREMENT_UNIT= AVAILABLE_MEASUREMENT_UNITS[0]

    CHANNELS:dict[str,dict]={'Channel1':{'Main.Descriptor':18688,'Main.PV':256,'Main.Units':18709,'Main.Resolution':6145},
                             'Channel2':{'Main.Descriptor':18715,'Main.PV':260,'Main.Units':18736,'Main.Resolution':6273},
                             'Channel3':{'Main.Descriptor':18742,'Main.PV':264,'Main.Units':18763,'Main.Resolution':6401},
                             'Channel4':{'Main.Descriptor':18769,'Main.PV':268,'Main.Units':18790,'Main.Resolution':6529},
                             'loop1.Main.ActiveOut':{'Main.PV':516},
                             'loop2.Main.ActiveOut':{'Main.PV':654}}

    LOOPS:dict[str,dict]={'Loop1':{'PID.SchedulerType':5685,'Main.PV':512,'Main.TargetSP':514,'Main.AutoMan':513,
                                   'Main.ActiveOut':516},
                          'Loop2':{'PID.SchedulerType':5941,'Main.PV':640,'Main.TargetSP':642,'Main.AutoMan':641,
                                   'Main.ActiveOut':654}}

    SETTINGS = {
        'DigitalIO': {
            '1A1B.PV': {'value': 5377, 'type': 'int'},
            '1A1B.TypeIO': {'value': 5376, 'type': 'int'},
            '1A1B.Invert': {'value': 5379, 'type': 'int'},
            '1A1B.Output': {'value': 5380, 'type': 'int'},
            '1A1B.Inertia': {'value': 5383, 'type': 'int'},
            '1A1B.Backlash': {'value': 5384, 'type': 'int'},
            '1A1B.StandbyAction': {'value': 5385, 'type': 'int'},
            '1A1B.ModuleIdent': {'value': 5386, 'type': 'int'},
            '2A2B.PV': {'value': 5393, 'type': 'int'},
            '2A2B.TypeIO': {'value': 5392, 'type': 'int'},
            '2A2B.Invert': {'value': 5395, 'type': 'int'},
            '2A2B.Output': {'value': 5396, 'type': 'int'},
            '2A2B.Inertia': {'value': 5399, 'type': 'int'},
            '2A2B.Backlash': {'value': 5400, 'type': 'int'},
            '2A2B.StandbyAction': {'value': 5401, 'type': 'int'},
            '2A2B.ModuleIdent': {'value': 5402, 'type': 'int'},
            'DI_LALC.PV': {'value': 5409, 'type': 'int'},
            'DI_LALC.TypeIO': {'value': 5408, 'type': 'int'},
            'DI_LALC.Invert': {'value': 5411, 'type': 'int'},
            'DI_LALC.Output': {'value': 5412, 'type': 'int'},
            'DI_LALC.Inertia': {'value': 5415, 'type': 'int'},
            'DI_LALC.Backlash': {'value': 5416, 'type': 'int'},
            'DI_LALC.StandbyAction': {'value': 5417, 'type': 'int'},
            'DI_LALC.ModuleIdent': {'value': 5418, 'type': 'int'},
            '3A3B.PV': {'value': 5425, 'type': 'int'},
            '3A3B.TypeIO': {'value': 5424, 'type': 'int'},
            '3A3B.Invert': {'value': 5427, 'type': 'int'},
            '3A3B.Output': {'value': 5428, 'type': 'int'},
            '3A3B.Inertia': {'value': 5431, 'type': 'int'},
            '3A3B.Backlash': {'value': 5432, 'type': 'int'},
            '3A3B.StandbyAction': {'value': 5433, 'type': 'int'},
            '3A3B.ModuleIdent': {'value': 5434, 'type': 'int'},
            'DI_LBLC.PV': {'value': 5441, 'type': 'int'},
            'DI_LBLC.TypeIO': {'value': 5440, 'type': 'int'},
            'DI_LBLC.Invert': {'value': 5443, 'type': 'int'},
            'DI_LBLC.Output': {'value': 5444, 'type': 'int'},
            'DI_LBLC.Inertia': {'value': 5447, 'type': 'int'},
            'DI_LBLC.Backlash': {'value': 5448, 'type': 'int'},
            'DI_LBLC.StandbyAction': {'value': 5449, 'type': 'int'},
            'DI_LBLC.ModuleIdent': {'value': 5450, 'type': 'int'},
            'RELAY_4AC.PV': {'value': 5457, 'type': 'int'},
            'RELAY_4AC.TypeIO': {'value': 5456, 'type': 'int'},
            'RELAY_4AC.Invert': {'value': 5459, 'type': 'int'},
            'RELAY_4AC.Output': {'value': 5460, 'type': 'int'},
            'RELAY_4AC.Inertia': {'value': 5463, 'type': 'int'},
            'RELAY_4AC.Backlash': {'value': 5464, 'type': 'int'},
            'RELAY_4AC.StandbyAction': {'value': 5465, 'type': 'int'},
            'RELAY_4AC.ModuleIdent': {'value': 5466, 'type': 'int'},
            'RELAY_5AC.PV': {'value': 5473, 'type': 'int'},
            'RELAY_5AC.TypeIO': {'value': 5472, 'type': 'int'},
            'RELAY_5AC.Invert': {'value': 5475, 'type': 'int'},
            'RELAY_5AC.Output': {'value': 5476, 'type': 'int'},
            'RELAY_5AC.Inertia': {'value': 5479, 'type': 'int'},
            'RELAY_5AC.Backlash': {'value': 5480, 'type': 'int'},
            'RELAY_5AC.StandbyAction': {'value': 5481, 'type': 'int'},
            'RELAY_5AC.ModuleIdent': {'value': 5482, 'type': 'int'},
        },
        'DCOutput': {
            '3A3B_DCOP.Type': {'value': 5536, 'type': 'int'},
            '3A3B_DCOP.PV': {'value': 5537, 'type': 'int'},
            '3A3B_DCOP.Status': {'value': 5538, 'type': 'int'},
            '3A3B_DCOP.Resolution': {'value': 5540, 'type': 'int'},
            '3A3B_DCOP.OutputLow': {'value': 5541, 'type': 'int'},
            '3A3B_DCOP.OutputHigh': {'value': 5542, 'type': 'int'},
            '3A3B_DCOP.ScaleLow': {'value': 5543, 'type': 'int'},
            '3A3B_DCOP.ScaleHigh': {'value': 5544, 'type': 'int'},
            '3A3B_DCOP.FallbackPV': {'value': 5545, 'type': 'int'},
            '3A3B_DCOP.MeasuredValue': {'value': 5546, 'type': 'int'},
            '2A2B_DCOP.Type': {'value': 5552, 'type': 'int'},
            '2A2B_DCOP.PV': {'value': 5553, 'type': 'int'},
            '2A2B_DCOP.Status': {'value': 5554, 'type': 'int'},
            '2A2B_DCOP.Resolution': {'value': 5556, 'type': 'int'},
            '2A2B_DCOP.OutputLow': {'value': 5557, 'type': 'int'},
            '2A2B_DCOP.OutputHigh': {'value': 5558, 'type': 'int'},
            '2A2B_DCOP.ScaleLow': {'value': 5559, 'type': 'int'},
            '2A2B_DCOP.ScaleHigh': {'value': 5560, 'type': 'int'},
            '2A2B_DCOP.FallbackPV': {'value': 5561, 'type': 'int'},
            '2A2B_DCOP.MeasuredValue': {'value': 5562, 'type': 'int'},
            '1A1B_DCOP.Type': {'value': 5568, 'type': 'int'},
            '1A1B_DCOP.PV': {'value': 5569, 'type': 'int'},
            '1A1B_DCOP.Status': {'value': 5570, 'type': 'int'},
            '1A1B_DCOP.Resolution': {'value': 5572, 'type': 'int'},
            '1A1B_DCOP.OutputLow': {'value': 5573, 'type': 'int'},
            '1A1B_DCOP.OutputHigh': {'value': 5574, 'type': 'int'},
            '1A1B_DCOP.ScaleLow': {'value': 5575, 'type': 'int'},
            '1A1B_DCOP.ScaleHigh': {'value': 5576, 'type': 'int'},
            '1A1B_DCOP.FallbackPV': {'value': 5577, 'type': 'int'},
            '1A1B_DCOP.MeasuredValue': {'value': 5578, 'type': 'int'},
        },
        'Instrument': {
            'Instrument.Info.Name': {'value': 17503, 'type': 'str'},
            'Instrument.Info.Type': {'value': 4258, 'type': 'int'},
            'Instrument.Info.Version': {'value': 17524, 'type': 'str'},
            'Instrument.IOFitted.1A1B': {'value': 4340, 'type': 'int'},
            'Instrument.IOFitted.2A2B': {'value': 4341, 'type': 'int'},
            'Instrument.IOFitted.3A3B': {'value': 4343, 'type': 'int'},
            'Instrument.IOFitted.4AC': {'value': 4345, 'type': 'int'},
            'Instrument.IOFitted.5AC': {'value': 4346, 'type': 'int'},
            'Instrument.IOFitted.LALC': {'value': 4342, 'type': 'int'},
            'Instrument.IOFitted.LBLC': {'value': 4344, 'type': 'int'},
        },
        'Loops': {
            'Loop1': {
                'Main.PV': {'value': 512, 'type': 'int'},
                'Main.TargetSP': {'value': 514, 'type': 'int'},
                'Main.WorkingSP': {'value': 515, 'type': 'int'},
                'Main.AutoMan': {'value': 513, 'type': 'int'}, #???
                'Main.ActiveOut': {'value': 516, 'type': 'int'},
                'Diag.TargetOutVal': {'value': 526, 'type': 'int'},
                'Diag.LoopBreakAlarm': {'value': 527, 'type': 'int'},
                'Diag.PropOutContrib': {'value': 528, 'type': 'int'},
                'Diag.IntegralOutContrib': {'value': 529, 'type': 'int'},
                'Diag.DerivativeOutContrib': {'value': 530, 'type': 'int'},
                'Diag.WrkOPLo': {'value': 532, 'type': 'int'},
                'Diag.WrkOPHi': {'value': 533, 'type': 'int'},
                'Diag.LoopMode': {'value': 5777, 'type': 'int'},
                'Diag.SchedPB': {'value': 5778, 'type': 'int'},
                'Diag.SchedTi': {'value': 5779, 'type': 'int'},
                'Diag.SchedTd': {'value': 5780, 'type': 'int'},
                'Diag.SchedCBH': {'value': 5781, 'type': 'int'},
                'Diag.SchedCBL': {'value': 5782, 'type': 'int'},
                'Diag.SchedOPHi': {'value': 5786, 'type': 'int'},
                'Diag.SchedOPLo': {'value': 5787, 'type': 'int'},
                'OP.OutputHighLimit': {'value': 5741, 'type': 'int'},
                'OP.OutputLowLimit': {'value': 5742, 'type': 'int'},
                'OP.Rate': {'value': 5744, 'type': 'int'},
                'OP.ManualMode': {'value': 5759, 'type': 'int'},
                'OP.ManualOutVal': {'value': 5760, 'type': 'int'},
                'OP.ForcedOP': {'value': 5775, 'type': 'int'},
                'OP.ManStartup': {'value': 5776, 'type': 'int'},
                'PID.NumSets': {'value': 5686, 'type': 'int'},
                'PID.ActiveSet': {'value': 5688, 'type': 'int'},
                'PID.Boundary1-2': {'value': 5689, 'type': 'int'},
                'PID.Boundary2-3': {'value': 5690, 'type': 'int'},
                'PID.ProportionalBand': {'value': 5691, 'type': 'int'},
                'PID.IntegralTime': {'value': 5692, 'type': 'int'},
                'PID.DerivativeTime': {'value': 5693, 'type': 'int'},
                'PID.CutbackHigh': {'value': 5695, 'type': 'int'},
                'PID.CutbackLow': {'value': 5696, 'type': 'int'},
                'PID.LoopBreakTime': {'value': 5698, 'type': 'int'},
                'PID.ProportionalBand2': {'value': 5699, 'type': 'int'},
                'PID.IntegralTime2': {'value': 5700, 'type': 'int'},
                'PID.DerivativeTime2': {'value': 5701, 'type': 'int'},
                'PID.CutbackHigh2': {'value': 5703, 'type': 'int'},
                'PID.CutbackLow2': {'value': 5704, 'type': 'int'},
                'PID.LoopBreakTime2': {'value': 5706, 'type': 'int'},
                'PID.ProportionalBand3': {'value': 5707, 'type': 'int'},
                'PID.IntegralTime3': {'value': 5708, 'type': 'int'},
                'PID.DerivativeTime3': {'value': 5709, 'type': 'int'},
                'PID.CutbackHigh3': {'value': 5711, 'type': 'int'},
                'PID.CutbackLow3': {'value': 5712, 'type': 'int'},
                'PID.LoopBreakTime3': {'value': 5714, 'type': 'int'},
                'PID.OutputLo': {'value': 5716, 'type': 'int'},
                'PID.OutputHi': {'value': 5715, 'type': 'int'},
                'PID.OutputLo2': {'value': 5718, 'type': 'int'},
                'PID.OutputHi2': {'value': 5717, 'type': 'int'},
                'PID.OutputLo3': {'value': 5720, 'type': 'int'},
                'PID.OutputHi3': {'value': 5719, 'type': 'int'},
                'PID.SchedulerType': {'value': 5685, 'type': 'int'},
                'Setup.CH1ControlType': {'value': 5633, 'type': 'int'},
                'Setup.CH2ControlType': {'value': 5634, 'type': 'int'},
                'Setup.PBUnits': {'value': 5636, 'type': 'int'},
                'SP.RangeLow': {'value': 5722, 'type': 'int'},
                'SP.RangeHigh': {'value': 5721, 'type': 'int'},
                'SP.Rate': {'value': 5730, 'type': 'int'},
                'SP.RateDisable': {'value': 5731, 'type': 'int'},
            },
            'Loop2': {
                'Main.PV': {'value': 640, 'type': 'int'},
                'Main.TargetSP': {'value': 642, 'type': 'int'},
                'Main.WorkingSP': {'value': 643, 'type': 'int'},
                'Main.AutoMan': {'value': 641, 'type': 'int'}, #???
                'Main.ActiveOut': {'value': 644, 'type': 'int'},
                'Diag.TargetOutVal': {'value': 654, 'type': 'int'},
                'Diag.LoopBreakAlarm': {'value': 655, 'type': 'int'},
                'Diag.PropOutContrib': {'value': 656,  'type': 'int'},
                'Diag.IntegralOutContrib': {'value': 657, 'type': 'int'},
                'Diag.DerivativeOutContrib': {'value': 658, 'type': 'int'},
                'Diag.WrkOPLo': {'value': 660,  'type': 'int'},
                'Diag.WrkOPHi': {'value': 661, 'type': 'int'},
                'Diag.LoopMode': {'value': 6033, 'type': 'int'},
                'Diag.SchedPB': {'value': 6034, 'type': 'int'},
                'Diag.SchedTi': {'value': 6035, 'type': 'int'},
                'Diag.SchedTd': {'value': 6036,  'type': 'int'},
                'Diag.SchedCBH': {'value': 6037, 'type': 'int'},
                'Diag.SchedCBL': {'value': 6038, 'type': 'int'},
                'Diag.SchedOPHi': {'value': 6042, 'type': 'int'},
                'Diag.SchedOPLo': {'value': 6043, 'type': 'int'},
                'OP.OutputHighLimit': {'value': 5997, 'type': 'int'},
                'OP.OutputLowLimit': {'value': 5998, 'type': 'int'},
                'OP.Rate': {'value': 6000, 'type': 'int'},
                'OP.ManualMode': {'value': 6015, 'type': 'int'},
                'OP.ManualOutVal': {'value': 6016, 'type': 'int'},
                'OP.ForcedOP': {'value': 6031, 'type': 'int'},
                'OP.ManStartup': {'value': 6032, 'type': 'int'},
                'PID.NumSets': {'value': 5942, 'type': 'int'},
                'PID.ActiveSet': {'value': 5944, 'type': 'int'},
                'PID.Boundary1-2': {'value': 5945, 'type': 'int'},
                'PID.Boundary2-3': {'value': 5946, 'type': 'int'},
                'PID.ProportionalBand': {'value': 5947, 'type': 'int'},
                'PID.IntegralTime': {'value': 5948, 'type': 'int'},
                'PID.DerivativeTime': {'value': 5949, 'type': 'int'},
                'PID.CutbackHigh': {'value': 5951, 'type': 'int'},
                'PID.CutbackLow': {'value': 5952, 'type': 'int'},
                'PID.LoopBreakTime': {'value': 5954, 'type': 'int'},
                'PID.ProportionalBand2': {'value': 5955, 'type': 'int'},
                'PID.IntegralTime2': {'value': 5956, 'type': 'int'},
                'PID.DerivativeTime2': {'value': 5957, 'type': 'int'},
                'PID.CutbackHigh2': {'value': 5959, 'type': 'int'},
                'PID.CutbackLow2': {'value': 5960, 'type': 'int'},
                'PID.LoopBreakTime2': {'value': 5962, 'type': 'int'},
                'PID.ProportionalBand3': {'value': 5963, 'type': 'int'},
                'PID.IntegralTime3': {'value': 5964, 'type': 'int'},
                'PID.DerivativeTime3': {'value': 5965, 'type': 'int'},
                'PID.CutbackHigh3': {'value': 5967, 'type': 'int'},
                'PID.CutbackLow3': {'value': 5968, 'type': 'int'},
                'PID.LoopBreakTime3': {'value': 5970, 'type': 'int'},
                'PID.OutputLo': {'value': 5972, 'type': 'int'},
                'PID.OutputHi': {'value': 5971, 'type': 'int'},
                'PID.OutputLo2': {'value': 5974, 'type': 'int'},
                'PID.OutputHi2': {'value': 5973, 'type': 'int'},
                'PID.OutputLo3': {'value': 5976, 'type': 'int'},
                'PID.OutputHi3': {'value': 5975, 'type': 'int'},
                'PID.SchedulerType': {'value': 5941, 'type': 'int'},
                'Setup.CH1ControlType': {'value': 5889, 'type': 'int'},
                'Setup.CH2ControlType': {'value': 5890, 'type': 'int'},
                'Setup.PBUnits': {'value': 5892, 'type': 'int'},
                'SP.RangeLow': {'value': 5978, 'type': 'int'},
                'SP.RangeHigh': {'value': 5977, 'type': 'int'},
                'SP.Rate': {'value': 5986, 'type': 'int'},
                'SP.RateDisable': {'value': 5987, 'type': 'int'},
            },
        },
        'Channels': {
            'Channel1': {
                'Main.PV': {'value': 256, 'type': 'int'},
                'Main.Status': {'value': 257, 'type': 'int'},
                'Main.PV2': {'value': 272, 'type': 'int'},
                'Main.Status2': {'value': 273, 'type': 'int'},
                'Main.Type': {'value': 6144, 'type': 'int'}, #???
                'Main.Resolution': {'value': 6145, 'type': 'int'},
                'Main.LinType': {'value': 6150, 'type': 'int'}, #???
                'Main.RangeLow': {'value': 6151, 'type': 'int'},
                'Main.RangeHigh': {'value': 6152, 'type': 'int'},
                'Main.RangeUnits': {'value': 6153, 'type': 'int'}, #???
                'Main.ScaleLow': {'value': 6154, 'type': 'int'},
                'Main.ScaleHigh': {'value': 6155, 'type': 'int'},
                'Main.SensorBreakType': {'value': 6159, 'type': 'int'}, #???
                'Main.SensorBreakVal': {'value': 6161, 'type': 'int'},
                'Main.MeasuredValue': {'value': 6164, 'type': 'int'},
                'Main.Offset': {'value': 6167, 'type': 'int'},
                'Main.Offset2': {'value': 6168, 'type': 'int'},
                'Main.MeasuredValue2': {'value': 6169, 'type': 'int'},
                'Main.ScaleLow2': {'value': 6170, 'type': 'int'},
                'Main.ScaleHigh2': {'value': 6171, 'type': 'int'},
                'Main.Units': {'value': 18709, 'type': 'int'},
                'Alarm1.Status': {'value': 258, 'type': 'int'},
                'Alarm1.Type': {'value': 6208, 'type': 'int'},
                'Alarm2.Status': {'value': 291, 'type': 'int'},
                'Alarm2.Type': {'value': 7264, 'type': 'int'},
                'Trend.Colour': {'value': 6176, 'type': 'int'},
            },
            'Channel2': {
                'Main.PV': {'value': 260, 'type': 'int'},
                'Main.Status': {'value': 261, 'type': 'int'},
                'Main.PV2': {'value': 276, 'type': 'int'},
                'Main.Status2': {'value': 277, 'type': 'int'},
                'Main.Type': {'value': 6272, 'type': 'int'}, #???
                'Main.Resolution': {'value': 6273, 'type': 'int'},
                'Main.LinType': {'value': 6278, 'type': 'int'}, #???
                'Main.RangeLow': {'value': 6279, 'type': 'int'},
                'Main.RangeHigh': {'value': 6280, 'type': 'int'},
                'Main.RangeUnits': {'value': 6281, 'type': 'int'}, #???
                'Main.ScaleLow': {'value': 6282, 'type': 'int'},
                'Main.ScaleHigh': {'value': 6283, 'type': 'int'},
                'Main.SensorBreakType': {'value': 6287, 'type': 'int'}, #???
                'Main.SensorBreakVal': {'value': 6289, 'type': 'int'},
                'Main.MeasuredValue': {'value': 6292, 'type': 'int'},
                'Main.Offset': {'value': 6295, 'type': 'int'},
                'Main.Offset2': {'value': 6296, 'type': 'int'},
                'Main.MeasuredValue2': {'value': 6297, 'type': 'int'},
                'Main.ScaleLow2': {'value': 6298, 'type': 'int'},
                'Main.ScaleHigh2': {'value': 6299, 'type': 'int'},
                'Main.Units': {'value': 18736, 'type': 'int'},
                'Alarm1.Status': {'value': 262, 'type': 'int'},
                'Alarm1.Type': {'value': 7360, 'type': 'int'},
                'Alarm2.Status': {'value': 295, 'type': 'int'},
                'Alarm2.Type': {'value': 7392, 'type': 'int'},
                'Trend.Colour': {'value': 6304, 'type': 'int'},
            },
            'Channel3': {
                'Main.PV': {'value': 264, 'type': 'int'},
                'Main.Status': {'value': 265, 'type': 'int'},
                'Main.PV2': {'value': 280, 'type': 'int'},
                'Main.Status2': {'value': 281, 'type': 'int'},
                'Main.Type': {'value': 6400, 'type': 'int'}, #???
                'Main.Resolution': {'value': 6401, 'type': 'int'},
                'Main.LinType': {'value': 6406, 'type': 'int'}, #???
                'Main.RangeLow': {'value': 6407, 'type': 'int'},
                'Main.RangeHigh': {'value': 6408, 'type': 'int'},
                'Main.RangeUnits': {'value': 6409, 'type': 'int'}, #???
                'Main.ScaleLow': {'value': 6410, 'type': 'int'},
                'Main.ScaleHigh': {'value': 6411, 'type': 'int'},
                'Main.SensorBreakType': {'value': 6415, 'type': 'int'}, #???
                'Main.SensorBreakVal': {'value': 6417, 'type': 'int'},
                'Main.MeasuredValue': {'value': 6420, 'type': 'int'},
                'Main.Offset': {'value': 6423, 'type': 'int'},
                'Main.Offset2': {'value': 6424, 'type': 'int'},
                'Main.MeasuredValue2': {'value': 6425, 'type': 'int'},
                'Main.ScaleLow2': {'value': 6426, 'type': 'int'},
                'Main.ScaleHigh2': {'value': 6427, 'type': 'int'},
                'Main.Units': {'value': 18763, 'type': 'int'},
                'Alarm1.Status': {'value': 266, 'type': 'int'},
                'Alarm1.Type': {'value': 6464, 'type': 'int'},
                'Alarm2.Status': {'value': 299, 'type': 'int'},
                'Alarm2.Type': {'value': 7520, 'type': 'int'},
                'Trend.Colour': {'value': 6432, 'type': 'int'},
            },
            'Channel4': {
                'Main.PV': {'value': 268, 'type': 'int'},
                'Main.Status': {'value': 269, 'type': 'int'},
                'Main.PV2': {'value': 284, 'type': 'int'},
                'Main.Status2': {'value': 285, 'type': 'int'},
                'Main.Type': {'value': 6528, 'type': 'int'}, #???
                'Main.Resolution': {'value': 6529, 'type': 'int'},
                'Main.LinType': {'value': 6354, 'type': 'int'}, #???
                'Main.RangeLow': {'value': 6535, 'type': 'int'},
                'Main.RangeHigh': {'value': 6536, 'type': 'int'},
                'Main.RangeUnits': {'value': 6537, 'type': 'int'}, #???
                'Main.ScaleLow': {'value': 6538, 'type': 'int'},
                'Main.ScaleHigh': {'value': 6539, 'type': 'int'},
                'Main.SensorBreakType': {'value': 6543, 'type': 'int'}, #???
                'Main.SensorBreakVal': {'value': 6545, 'type': 'int'},
                'Main.MeasuredValue': {'value': 6548, 'type': 'int'},
                'Main.Offset': {'value': 6551, 'type': 'int'},
                'Main.Offset2': {'value': 6552, 'type': 'int'},
                'Main.MeasuredValue2': {'value': 6553, 'type': 'int'},
                'Main.ScaleLow2': {'value': 6554, 'type': 'int'},
                'Main.ScaleHigh2': {'value': 6555, 'type': 'int'},
                'Main.Units': {'value': 18790, 'type': 'int'},
                'Alarm1.Status': {'value': 270, 'type': 'int'},
                'Alarm1.Type': {'value': 6592, 'type': 'int'},
                'Alarm2.Status': {'value': 303, 'type': 'int'},
                'Alarm2.Type': {'value': 7648, 'type': 'int'},
                'Trend.Colour': {'value': 6560, 'type': 'int'},
            }
        }
    }
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
            info = f"Connection opened at ip : {self.ip}"
            sleep(0.2) # Make sure connection is established before doing anything else
        except ConnectionException as e:
            info = f"Failed to open connection at ip : {self.ip} \n {e}"
        opened = self.client.is_socket_open()
        return opened,info

    def get_current_value(self,address,typeVar='int',count=1):
        """once the instrument is initialized, return its current measured value"""

        # print(f"+++++++++++++++{address}================={typeVar}================{count}+++++++++++++")
        try:
            read = self.client.read_holding_registers(address=address, count=count)

        # except ConnectionException as e:
        #     print(f"Connection error: {e}")
        # except ModbusIOException as e:
        #     print(f"I/O error: {e}")
        # except ModbusException as e:
        #     print(f"Modbus error: {e}")
        except Exception as e:
            self.disconnect()
            self.connect()
            print(f"******  {e}  *******")
            # self.emit_status(ThreadCommand('Update_Status', [e]))
            # print(f"+++++++  {address}, {count}  +++")
            # print(f"+++++++++++++++{typeVar}+++++++++++++")
            # self.get_current_value(self, address, typeVar=typeVar, count=count)
            sleep(0.5)
            read = self.client.read_holding_registers(address=address, count=count)
            code = getattr(read, 'exception_code', None)
            if code:
                print(f"Exception code {code}")
            else:
                print(f"Error: {read}")
        if typeVar =='int':
            returnValue=read.registers[0]
        else:
            returnValue = ''.join(map(chr, list(filter(lambda num: num != 0, read.registers))))
        return returnValue

    def set_current_value(self,address,value):
        """once the instrument is initialized, set current  value for consign"""
        # print(address)
        try:
            write=self.client.write_register(address=address, value=value)
        except Exception as e:
            self.connect()
            write=self.client.write_register(address=address, value=value)
        return write


    def disconnect(self):
        self.client.close()
        return not self.client.is_socket_open()

    def get_instrument_display_units(self):
        """"""
        # print(f'{self}')
        value=self.get_current_value(address=self.CHANNELS['Channel1']['Main.Units'],typeVar='str', count=6)
        # print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{value}')
        self.unit=value

        return self.unit
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
# if __name__ == '__main__':
#     main(__file__, init=False)
 # if name == 'main':
 #    ip = '192.168.0.1'
 #    a = Nanodac(ip)
 #    opened, info = a.connect()
 #    if not opened:
 #        print(f"Nanodac Failed to open connection --> {info}")
 #    else:
 #        print(f"Nanodac connected --> {info}")
 #        ch = a.CHANNELS['Channel1']
 #        print('PV:', a.get_current_value(address=ch['Main.PV']))
 #        print('Unités:', a.get_instrument_display_units())
 #    print('NANODAC TESTING DONE!')