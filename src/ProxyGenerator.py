import importlib
import MayaUtils
importlib.reload(MayaUtils)

from MayaUtils import GetAllConnectionsIn, GetUpperStream, IsJoint, IsMesh, IsSkin, MayaWindow
from PySide2.QtWidgets import QLabel, QPushButton, QVBoxLayout
import maya.cmds as mc

class ProxyGenerator:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.joints = []

    def BuildProxyForSelectedMesh(self):
        model = mc.ls(sl=True)[0]
        if not IsMesh(model):
            print(f"{model} is not a mesh!")
            return
        
        self.model = model
        modelShape = mc.listRelatives(self.model, s=True)[0]
        skin = GetAllConnectionsIn(modelShape, GetUpperStream, IsSkin)
        if not skin:
            print(f"{self.model} is not bound")
            return
        
        joints = GetAllConnectionsIn(modelShape, GetUpperStream, IsJoint)
        if not joints:
            print(f"{self.model} is not bound with any joint")
            return
        
        self.skin = skin[0]
        self.joints = joints
        print(f"found model {self.model} with skin {self.skin} and joints {self.joints}")

        jointVertDict = self.GenerateJointVertsDict()
        chunks = []
        controls = []
        for jnt, vert in jointVertDict.items():
            newChuck = self.CreateProxyModelForJointAndVerts(jnt, vert)

    def CreateProxyModelForJointAndVerts(self, joint, verts):
        if not verts:
            return None
        
        faces = mc.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        faces = mc.ls(faces, fl=True)

        faceNames = set()
        for face in faces:
            faceNames.add(face.replace(self.model, ""))
            
        dup = mc.duplicate(self.model)[0]
        allDupFaces = mc.ls(f"{dup}.f[*]", fl=True)
        facesToDelete = []
        for dupFace in allDupFaces:
            if dupFace.replace(dup, "") not in faceNames:
                facesToDelete.append(dupFace)

        mc.delete(facesToDelete)
        dupName = self.model + "_" + joint + "_proxy"
        mc.rename(dup, dupName)
        return dupName

    def GenerateJointVertsDict(self):
        dict = {}
        for joint in self.joints:
            dict[joint] = []

        verts = mc.ls(f"{self.model}.vtx[*]", fl=True)
        for vert in verts:
            ownerJoint = self.GetJointWithMaxInfluence(vert, self.skin)
            dict[ownerJoint].append(vert)

        return dict

    def GetJointWithMaxInfluence(self, vert, skin):
        weights = mc.skinPercent(skin, vert, q=True, v=True)
        joints = mc.skinPercent(skin, vert, q=True, t=None)

        maxWeightIndex = 0
        maxWeight = weights[0]
        for i in range(1, len(weights)):
            if weights[i] > maxWeight:
                maxWeight = weights[i]
                maxWeightIndex = i

        return joints[maxWeightIndex]

class ProxyGeneratorWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.generator = ProxyGenerator()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.masterLayout.addWidget(QLabel("Please Select the Rigged Model and Press Build"))
        buildButton = QPushButton("Build")
        self.masterLayout.addWidget(buildButton)
        buildButton.clicked.connect(self.generator.BuildProxyForSelectedMesh)
        self.setWindowTitle("Proxy Generator")

    def GetWidgetUniqueName(self):
        return "fje8f[83j09skldnf4ht]dq-0"
    
ProxyGeneratorWidget().show()