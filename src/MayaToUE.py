import os
from MayaUtils import *
from PySide2.QtCore import Signal
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QCheckBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout
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
        self.subfix = ""
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

    def SendToUnreal(self):
        print("Sending to Unreal!")

    def GetSkeletalMeshSavePath(self):
        savePath = os.path.join(self.saveDir, self.fileName + ".fbx")
        return os.path.normpath(savePath)
    
    def GetAnimClipSavePath(self, animClip: AnimClip):
        savePath = os.path.join(self.saveDir, "animations", self.fileName + animClip.subfix + ".fbx")
        return os.path.normpath(savePath)

    def RemoveAnimClip(self, animClip: AnimClip):
        self.animations.remove(animClip)
        print(f"removed anim clip, now we have: {len(self.animations)} left")

    def AddNewAnimClip(self):
        self.animations.append(AnimClip())
        print(f"added anim clip, now we have: {len(self.animations)} clips")
        return self.animations[-1]

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

class AnimClipWidget(QWidget):
    animClipRemoved = Signal(AnimClip)
    animClipSubfixChange = Signal(str)
    def __init__(self, animClip: AnimClip):
        super().__init__()
        self.animClip = animClip
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        shouldExportCheckbox = QCheckBox()
        shouldExportCheckbox.setChecked(self.animClip.shouldExport)
        self.masterLayout.addWidget(shouldExportCheckbox)
        shouldExportCheckbox.toggled.connect(self.ShouldExportCheckboxToggled)

        #
        # Suffix
        #

        subfixLabel = QLabel("subfix: ")
        self.masterLayout.addWidget(subfixLabel)
        subfixLineEdit = QLineEdit()
        subfixLineEdit.setValidator(QRegExpValidator("\w+"))
        subfixLineEdit.setText(self.animClip.subfix)
        subfixLineEdit.textChanged.connect(self.subfixTextChanged)
        self.masterLayout.addWidget(subfixLineEdit)

        #
        # min Frame
        #

        minFrameLabel = QLabel("Min: ")
        self.masterLayout.addWidget(minFrameLabel)
        minFrameLineEdit = QLineEdit()
        minFrameLineEdit.setValidator(QIntValidator())
        minFrameLineEdit.setText(str(int(self.animClip.frameMin)))
        minFrameLineEdit.textChanged.connect(self.MinFrameChanged)
        self.masterLayout.addWidget(minFrameLineEdit)

        #
        # Max Frame
        #

        maxFrameLabel = QLabel("max: ")
        self.masterLayout.addWidget(maxFrameLabel)
        maxFrameLineEdit = QLineEdit()
        maxFrameLineEdit.setValidator(QIntValidator())
        maxFrameLineEdit.setText(str(int(self.animClip.frameMax)))
        maxFrameLineEdit.textChanged.connect(self.MaxFrameChanged)
        self.masterLayout.addWidget(maxFrameLineEdit)

        #
        # Set Range
        #

        setRangeBtn = QPushButton("[-]")
        setRangeBtn.clicked.connect(self.SetRangeBtnClicked)
        self.masterLayout.addWidget(setRangeBtn)

        #
        # Delete
        #

        deleteBtn = QPushButton("X")
        deleteBtn.clicked.connect(self.DeleteBtnClicked)
        self.masterLayout.addWidget(deleteBtn)

    def DeleteBtnClicked(self):
        self.animClipRemoved.emit(self.animClip)
        self.deleteLater()

    def SetRangeBtnClicked(self):
        mc.playbackOptions(e=True, min=self.animClip.frameMin, max=self.animClip.frameMax)
        mc.playbackOptions(e=True, ast=self.animClip.frameMin, aet=self.animClip.frameMax)

    def MinFrameChanged(self, newVal):
        self.animClip.frameMin = int(newVal)

    def MaxFrameChanged(self, newVal):
        self.animClip.frameMax = int(newVal)

    def subfixTextChanged(self, newText):
        self.animClip.subfix = newText
        self.animClipSubfixChange.emit(newText)

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

        addAnimEntryBtn = QPushButton("Add Animation Clip")
        addAnimEntryBtn.clicked.connect(self.AddAnimEntryBtnClicked)
        self.masterLayout.addWidget(addAnimEntryBtn)

        self.animClipEntryLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.animClipEntryLayout)

        self.saveFileLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.saveFileLayout)

        self.saveFileLayout.addWidget(QLabel("Filename: "))
        self.fileNameLineEdit = QLineEdit()
        self.fileNameLineEdit.setFixedWidth(100)
        self.fileNameLineEdit.setValidator(QRegExpValidator("\w+"))
        self.fileNameLineEdit.textChanged.connect(self.FileNameLineEditChanged)
        self.saveFileLayout.addWidget(self.fileNameLineEdit)

        self.saveFileLayout.addWidget(QLabel("Save Directory: "))
        self.saveDirectoryLineEdit = QLineEdit()
        self.saveDirectoryLineEdit.setEnabled(False)
        self.saveFileLayout.addWidget(self.saveDirectoryLineEdit)

        self.pickDirectoryButton = QPushButton("...")
        self.pickDirectoryButton.clicked.connect(self.PickDirectoryButtonClicked)
        self.saveFileLayout.addWidget(self.pickDirectoryButton)

        self.savePreviewLabel = QLabel()
        self.masterLayout.addWidget(self.savePreviewLabel)

        sendToUEButton = QPushButton("Send to Unreal")
        sendToUEButton.clicked.connect(self.mayaToUE.SendToUnreal)
        self.masterLayout.addWidget(sendToUEButton)

    def UpdateSavePreviewLabel(self):
        previewText = self.mayaToUE.GetSkeletalMeshSavePath()
        for animClip in self.mayaToUE.animations:
            animSavePath = self.mayaToUE.GetAnimClipSavePath(animClip)
            previewText += "\n" + animSavePath

        self.savePreviewLabel.setText(previewText)

    def PickDirectoryButtonClicked(self):
        pickedPath = QFileDialog().getExistingDirectory()
        self.saveDirectoryLineEdit.setText(pickedPath)
        self.mayaToUE.saveDir = pickedPath
        self.UpdateSavePreviewLabel()

    def FileNameLineEditChanged(self, newVal):
        self.mayaToUE.fileName = newVal
        self.UpdateSavePreviewLabel()
    
    @TryAction
    def AddAnimEntryBtnClicked(self):
        newAnimClip = self.mayaToUE.AddNewAnimClip()
        newAnimClipWidget = AnimClipWidget(newAnimClip)
        newAnimClipWidget.animClipRemoved.connect(self.AnimationClipRemoved)
        newAnimClipWidget.animClipSubfixChange.connect(lambda *arg : self.UpdateSavePreviewLabel())
        self.animClipEntryLayout.addWidget(newAnimClipWidget)
        self.UpdateSavePreviewLabel()

    @TryAction
    def AnimationClipRemoved(self, animClip: AnimClip):
        self.mayaToUE.RemoveAnimClip(animClip)
        self.UpdateSavePreviewLabel()

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

MayaToUEWidget().show()
#AnimClipWidget(AnimClip()).show()