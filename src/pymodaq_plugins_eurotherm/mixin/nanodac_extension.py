from qtpy import QtWidgets, QtCore
from pymodaq_utils.utils import ThreadCommand


class NanodacShowParamMixin:
    """Mixin : ajoute showParam à tout plugin ayant self.controller (Nanodac)."""

    def showParam(self, param, param2=None):
        """Ouvre une fenêtre avec les valeurs du Nanodac en lecture seule."""
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle(f"Nanodac – {param}")
        dlg.setFixedWidth( 800)
        scrollable = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(scrollable)
        if param2 is None:
            dictSettings = self.controller.SETTINGS[param]
        else:
            if param2!="loop1.Main.ActiveOut" and param2!="loop2.Main.ActiveOut":
                dictSettings = self.controller.SETTINGS[param][param2]
            else:
                dictSettings={}
        if dictSettings=={}:
            form.addRow(f" info {param}: ", QtWidgets.QLabel(f" no data available for {param2}"))
        else:
            for paramName in dictSettings:
                typeVar = dictSettings[paramName]['type']
                count = 6 if typeVar == 'str' else 3
                value = self.controller.get_current_value(
                    address=dictSettings[paramName]['value'],
                    typeVar=typeVar, count=count)
                form.addRow(f"{paramName} : ", QtWidgets.QLabel(str(value)))
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(scrollable)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        dlg_layout = QtWidgets.QVBoxLayout(dlg)
        dlg_layout.addWidget(scroll)

        self.emit_status(ThreadCommand('Update_Status', [f'show pop-up param  {param}']))
        dlg.exec()