from PySide2.QtWidgets import QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
from PySide2.QtCore import Qt
import maya.OpenMayaUI as OpenMayaUI
import shiboken2
import maya.cmds as mc

def GetMayaMainWindow()->QMainWindow:
    mainWindow = OpenMayaUI.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow)

def DeleteWidgetWithName(name)->QMainWindow:
    for widget in GetMayaMainWindow().findChildren(QWidget, name):
        widget.deleteLater()

class MayaWindow(QWidget):
    def __init__(self):
        super().__init__(parent = GetMayaMainWindow())
        DeleteWidgetWithName(self.GetWidgetUniqueName())
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWidgetUniqueName())

    def GetWidgetUniqueName(self):
        return "djsiofsklfhawp98ahw389dfnseiof"

class LimbRigger:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 2

    def FindJointsBasedOnSelection(self):
        try:
            #gets selected joint
            self.root = mc.ls(sl=True, type="joint")[0]

            #gets first child of selection
            self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
            self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]
        except Exception as e:
            raise Exception("Invalid Selection, please select the first joint of the limb")

    def CreateFKControllerForJoint(self, jntName):
        ctrlName = "ac_L_fk" + jntName
        ctrlGrpName = ctrlName + "_grp"
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0))
        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName
    
    def RigLimb(self):
        rootCtrl, rootCtrlGrp = self.CreateFKControllerForJoint(self.root)
        midCtrl, midCtrlGrp = self.CreateFKControllerForJoint(self.mid)
        endCtrl, endCtrlGrp = self.CreateFKControllerForJoint(self.end)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, midCtrl)


class LimbRiggerWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.rigger = LimbRigger()

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        toolTipLabel = QLabel("Select the first joint of the limb and press the auto find button")
        self.masterLayout.addWidget(toolTipLabel)

        self.jointsListLineEdit = QLineEdit()
        self.masterLayout.addWidget(self.jointsListLineEdit)
        self.jointsListLineEdit.setEnabled(False)

        autoFindJointButton = QPushButton("Auto Find Joint")
        autoFindJointButton.clicked.connect(self.AutoFindJointButtonClicked)
        self.masterLayout.addWidget(autoFindJointButton)

        rigLimbButton = QPushButton("Rig Limb")
        rigLimbButton.clicked.connect(lambda : self.rigger.RigLimb())
        self.masterLayout.addWidget(rigLimbButton)

    def AutoFindJointButtonClicked(self):
        try:
            self.rigger.FindJointsBasedOnSelection()
            self.jointsListLineEdit.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{e}")

limbRiggerWidget = LimbRiggerWidget()
limbRiggerWidget.show()