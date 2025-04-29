import sys

projectPath = "C:/Github/MayaPlugins/src"
moduleDir = "C:/Github"

if projectPath not in sys.path:
    sys.path.append(projectPath)

if moduleDir not in sys.path:
    sys.path.append(moduleDir)