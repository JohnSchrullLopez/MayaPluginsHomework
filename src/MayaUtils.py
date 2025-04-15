from PySide2.QtWidgets import QMainWindow, QWidget #this imports all ui widget we are going to use
from PySide2.QtCore import Qt
import maya.OpenMayaUI as omui
import shiboken2

def GetMayaMainWindow()->QMainWindow:
    mainWindow = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow)

def DeleteWidgetWithName(name):
    for widget in GetMayaMainWindow().findChildren(QWidget, name):
        widget.deleteLater()

class MayaWindow(QWidget):
    def __init__(self):
        super().__init__(parent = GetMayaMainWindow())
        DeleteWidgetWithName(self.GetWidgetUniqueName())
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWidgetUniqueName())

    def GetWidgetUniqueName(self):
        return "dsfsdfsdfisdfhsdlfie34234hdsi34hsdfi"