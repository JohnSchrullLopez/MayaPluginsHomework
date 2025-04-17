# My Maya Plugins

## Limb Rigger

<img src="./assets/borzoi-overview.jpg">

[Limb Rigger]("src/LimbRigger.py)
this plugin rigs 3 any jointed limb with ik and fk with blend.

* support auto joint finding
* controller size controlv
* controller color control 

# Proxy Generator
explain how it works
what the tool does for now
explain classes, functions, and the logic

    for dupFace in allDupFaces:
        if dupFace.replace(dup, "") not in faceNames:
            facesToDelete.append(dupFace)

## BuildProxyForSelectedMesh()
* Checks if selected object is a mesh then get the model, shape, and skin from selection using the [GetAllConnectionsIn](#getallconnectionsin) function
* Generates a dictionary using the [GenerateJointVertsDict](#generatejointvertsdict) function where the keys are joints and the values are the vertices controlling the joint
* Calls the [CreateProxyModelForJointsAndVerts](#createproxymodelforjointsandverts) functions using the joint/vert dictionary

## GetAllConnectionsIn()
* Iterates through up to 100 of the upper or lowers stream node connections of an object
* Recursively calls an upper or lower stream get function and adds only unique connections
* Filters out objects that are unwanted using a function to check connection type

## GenerateJointVertsDict()
* Loop through all of the joints found earlier and assign them to the keys of a dictionary
* Get all vertices of the model by accessing the model's vertex array with a wildcard operator

        verts = mc.ls(f"{self.model}.vtx[*]", fl=True)
* loop through each vertex and get the joint that has the max influence on it using the [GetJointWithMaxInfluence](#getjointwithmaxinfluence) function. Append this vertex to the joint with the max influence in the dictionary.

## CreateProxyModelForJointsAndVerts()
* Convert mesh vertices to faces
* Strip model name from all of the faces

        faceNames = set()
            for face in faces:
                faceNames.add(face.replace(self.model, ""))
* Duplicate the model and get its faces. Add faces that will be deleted to an array.

        dup = mc.duplicate(self.model)[0]
            allDupFaces = mc.ls(f"{dup}.f[*]", fl=True)
            facesToDelete = []
            for dupFace in allDupFaces:
                if dupFace.replace(dup, "") not in faceNames:
                    facesToDelete.append(dupFace)
* Delete the "faces to delete" array

## GetJointWithMaxInfluence()
* Get a list of joints and the weight for the current joint and vertex 

        weights = mc.skinPercent(skin, vert, q=True, v=True)
            joints = mc.skinPercent(skin, vert, q=True, t=None)

* loop through list of weights and return the joint with the highest weight
