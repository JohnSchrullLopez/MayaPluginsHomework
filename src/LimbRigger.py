from PySide2.QtWidgets import QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget #import classes from the QtWidgets module
from PySide2.QtCore import Qt #Import Qt class from QtCore
import maya.OpenMayaUI as OpenMayaUI #Import Maya UI module
import shiboken2 #Import shoken2
import maya.cmds as mc #Import maya commands

def GetMayaMainWindow()->QMainWindow: #Defines the GetMayaMainWindow() function that returns QMainWindow
    mainWindow = OpenMayaUI.MQtUtil.mainWindow() #Instantiate a mainWindow() class and assign to mainWindow
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow) #Create python wrapper for a QMainWindow object

def DeleteWidgetWithName(name)->QMainWindow: #Defines the DeleteWidgetWithName() function that returns QMainWindow
    for widget in GetMayaMainWindow().findChildren(QWidget, name): #Loop through children of type QWidget with name in main maya window
        widget.deleteLater() #Delete widget when event loop has control

class MayaWindow(QWidget): #Define class MayaWindow 
    def __init__(self): #Constructor
        super().__init__(parent = GetMayaMainWindow()) #Parent this window to main maya window
        DeleteWidgetWithName(self.GetWidgetUniqueName()) #Delete old widget if it exists
        self.setWindowFlags(Qt.WindowType.Window) #Make widget a window
        self.setObjectName(self.GetWidgetUniqueName()) #Set object name as unique identifier

    def GetWidgetUniqueName(self): #Defines GetWidgetUniqueName() function
        return "djsiofsklfhawp98ahw389dfnseiof" #Returns unique identifier for this widget

class LimbRigger: #Define LimbRigger class
    def __init__(self): #Initializer
        self.root = "" #Clear root joint
        self.mid = "" #Clear mid joint
        self.end = "" #Clear end joint
        self.controllerSize = 2 #Set size of controller to 2

    def FindJointsBasedOnSelection(self): #Define the FindJointsBasedOnSelection function
        try: #Check for errors
            self.root = mc.ls(sl=True, type="joint")[0] #Gets currently selected joint and assigns it to root

            self.mid = mc.listRelatives(self.root, c=True, type="joint")[0] #gets first child of root and assigns it to mid
            self.end = mc.listRelatives(self.mid, c=True, type="joint")[0] #gets first child of mid and assigns it to end
        except Exception as e: #Handle errors
            raise Exception("Invalid Selection, please select the first joint of the limb") #Display error 

    def CreateFKControllerForJoint(self, jntName): #Define CreateFKControllerForJoint Function
        ctrlName = "ac_L_fk" + jntName #Set control name to prefix + jntName
        ctrlGrpName = ctrlName + "_grp" #Set group name to ctrlName + suffix
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0)) #Create a nurb circle and set name, size, and orientation
        mc.group(ctrlName, n=ctrlGrpName) #Group ctrl to ctrlGrp
        mc.matchTransform(ctrlGrpName, jntName) #Match ctrlGrp to joint transform
        mc.orientConstraint(ctrlName, jntName) #Match orientation of control to joint
        return ctrlName, ctrlGrpName #Return control and control group
    
    def RigLimb(self): #Defines RigLimb function
        rootCtrl, rootCtrlGrp = self.CreateFKControllerForJoint(self.root) #Creates FK controller for root joint
        midCtrl, midCtrlGrp = self.CreateFKControllerForJoint(self.mid) #Creates FK controller for mid joint 
        endCtrl, endCtrlGrp = self.CreateFKControllerForJoint(self.end) #Creates FK controller for end joint

        mc.parent(midCtrlGrp, rootCtrl) #Parent mid control group to root controller
        mc.parent(endCtrlGrp, midCtrl) #Parent end control group to mid controller


class LimbRiggerWidget(MayaWindow): #Define LimbRiggerWidget
    def __init__(self): #Initializer
        super().__init__() #Call base class initializer
        self.rigger = LimbRigger() #Make new LimbRigger object

        self.masterLayout = QVBoxLayout() #Create QVBoxLayout object and assign to masterLayout
        self.setLayout(self.masterLayout) #set layout to masterLayout

        toolTipLabel = QLabel("Select the first joint of the limb and press the auto find button") #Create tooltip
        self.masterLayout.addWidget(toolTipLabel) #Add tooltip widget to window

        self.jointsListLineEdit = QLineEdit() #Create QLineEdit object, a one line text editor
        self.masterLayout.addWidget(self.jointsListLineEdit) #Add line edit widget to master Layout
        self.jointsListLineEdit.setEnabled(False) #Disable editing of line edit

        autoFindJointButton = QPushButton("Auto Find Joint") #Create QPushButton object with text
        autoFindJointButton.clicked.connect(self.AutoFindJointButtonClicked) #Register AutoFindJointButtonClicked function to the clicked event
        self.masterLayout.addWidget(autoFindJointButton) #Add joint button widget to master layout

        rigLimbButton = QPushButton("Rig Limb") #Create Limb Rig button
        rigLimbButton.clicked.connect(lambda : self.rigger.RigLimb()) #Register RigLimb function to button clicked event
        self.masterLayout.addWidget(rigLimbButton) #Add widget to master layout

    def AutoFindJointButtonClicked(self): #Define AutoFindJointButtonClicked
        try: #Check for exception
            self.rigger.FindJointsBasedOnSelection() #Get joints based on currently selected joint. Calls the function from our rigger class
            self.jointsListLineEdit.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}") #Set text line to found joints
        except Exception as e: #Handle exceptions 
            QMessageBox.critical(self, "Error", f"{e}") #raise a critical error

limbRiggerWidget = LimbRiggerWidget() #Create LimbRiggerWidget object
limbRiggerWidget.show() #Show LimbRiggerWidget