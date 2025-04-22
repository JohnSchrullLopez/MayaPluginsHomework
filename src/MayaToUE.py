from MayaUtils import *
from PySide2.QtGui import QRegExpValidator
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout
import maya.cmds as mc

def TryAction(actionFunc):
    def wrapper(*args, **kwargs):
        try:
            actionFunc(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error", f"{e}")

    return wrapper

class AnimClip:
    def __init__(self):
        self.suffix = ""
        self.frameMin = mc.playbackOptions(q=True, min=True)
        self.frameMax = mc.playbackOptions(q=True, max=True)
        self.shouldExport = True

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.models = set()
        self.animations : list[AnimClip] = []
        self.fileName = ""
        self.saveDir = ""

    def AddSelectedMeshes(self):
        selection = mc.ls(sl=True)

        if not selection:
            raise Exception("No Mesh Selected. Select all the meshes of your rig")
        
        meshes = []
        for sel in selection:
            if IsMesh(sel):
                meshes.append(sel)

        if len(meshes) == 0:
            raise Exception("No Mesh Selected. Select all the meshes of your rig")
        
        self.models = meshes

    def SetSelectedJointAsRoot(self):
        selection = mc.ls(sl=True, type="joint")
        if not selection:
            raise Exception("Wrong Selection! Please Select the root joint of your rig!")
        
        self.rootJnt = selection[0]

    def AddRootJoint(self):
        if not self.rootJnt:
            raise Exception("No Root Joint Assigned, please set the root joint of your rig first")
        
        if mc.objExists(self.rootJnt):
            currentRootPos = mc.xform(self.rootJnt, q=True, ws=True, t=True)
            if currentRootPos[0] == 0 and currentRootPos[1] == 0 and currentRootPos[2] == 0:
                raise Exception("Current root joint is at the origin already, no need to make a new one!")
            
        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName

class AnimClipWidget(MayaWindow):
    def __init__(self, animClip: AnimClip):
        super().__init__()
        self.animClip = animClip
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        shouldExportCheckbox = QCheckBox()
        shouldExportCheckbox.setChecked(self.animClip.shouldExport)
        self.masterLayout.addWidget(shouldExportCheckbox)
        shouldExportCheckbox.toggled.connect(self.ShouldExportCheckboxToggled)

        suffixLabel = QLabel("Suffix: ")
        self.masterLayout.addWidget(suffixLabel)
        suffixLineEdit = QLineEdit()
        suffixLineEdit.setValidator(QRegExpValidator("[a-zA-Z0-9_]+"))
        suffixLineEdit.setText(self.animClip.suffix)
        suffixLineEdit.textChanged.connect(self.SuffixTextChanged)
        self.masterLayout.addWidget(suffixLineEdit)

    def SuffixTextChanged(self, newText):
        self.animClip.suffix = newText

    def ShouldExportCheckboxToggled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport

class MayaToUEWidget(MayaWindow):
    def GetWidgetUniqueName(self):
        return "MayaToUEWidgetJRSL4172025407"
    
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()

        self.setWindowTitle("Maya To UE")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectedAsRootJntBtn = QPushButton("Set Root Joint")
        setSelectedAsRootJntBtn.clicked.connect(self.SetSelectedAsRootJntBtnClicked)
        self.masterLayout.addWidget(setSelectedAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntBtnClicked)
        self.masterLayout.addWidget(addRootJntBtn)

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        self.meshList.setMaximumHeight(100)

        addMeshesBtn = QPushButton("Add Meshes")
        addMeshesBtn.clicked.connect(self.AddMeshesBtnClicked)
        self.masterLayout.addWidget(addMeshesBtn)

    @TryAction
    def AddMeshesBtnClicked(self):
        self.mayaToUE.AddSelectedMeshes()
        self.meshList.clear()
        self.meshList.addItems(self.mayaToUE.models)

    @TryAction
    def AddRootJntBtnClicked(self):
        self.mayaToUE.AddRootJoint()
        self.rootJntText.setText(self.mayaToUE.rootJnt)

    @TryAction
    def SetSelectedAsRootJntBtnClicked(self):
        self.mayaToUE.SetSelectedJointAsRoot()
        self.rootJntText.setText(self.mayaToUE.rootJnt)

#MayaToUEWidget().show()
AnimClipWidget(AnimClip()).show()