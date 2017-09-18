from qt import QtWidgets

try:
    from shiboken2 import wrapInstance as wrapinstance
except:
    from shiboken import wrapInstance as wrapinstance

import maya.OpenMayaUI as apiUI
from maya import cmds


def getMayaWindow():
    """
    :return: instance, the mainWindow ptr as a QmainWindow widget
    """
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapinstance(long(ptr), QtWidgets.QMainWindow)


def fullName(widget):
    return apiUI.MQtUtil.fullName(long(widget))


def getMayaWindowName():
    """Returns the maya window objectName from QT
    :return:
    """
    return getMayaWindow().objectName()


def toQtObject(mayaName):
    """Convert a Maya ui path to a Qt object.

    :param mayaName: Maya UI Path to convert
        (Ex: "scriptEditorPanel1Window|TearOffPane|scriptEditorPanel1|testButton" )
    :return: PyQt representation of that object
    """
    ptr = apiUI.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findMenuItem(mayaName)

    if ptr is not None:
        return wrapinstance(long(ptr), QtWidgets.QWidget)


def getOutliners():
    return [toQtObject(i) for i in cmds.getPanel(typ="outlinerPanel")]


def suppressOutput():
    """Supresses all output to the script editor
    """
    cmds.scriptEditorInfo(e=True,
                          suppressResults=True,
                          suppressErrors=True,
                          suppressWarnings=True,
                          suppressInfo=True)


def restoreOutput():
    """Restores the script editor to include all results
    """
    cmds.scriptEditorInfo(e=True,
                          suppressResults=False,
                          suppressErrors=False,
                          suppressWarnings=False,
                          suppressInfo=False)


def setChannelBoxAtTop(channelBox, value):
    """
    :param channelBox: mainChannelBox
    :type channelBox: str
    :param value:
    :type value: bool
    :example::
        setChannelBoxAtTop("mainChannelBox",True)
    """
    cmds.channelBox(channelBox, edit=True, containerAtTop=value)


def setChannelShowType(channelBox, value):
    """
    :param channelBox: mainChannelBox
    :type channelBox: str
    :param value:
    :type value: str
    :example::
        setChannelShowType("mainChannelBox", "all")
    """
    cmds.optionVar(stringValue=("cbShowType", value))
    cmds.channelBox(channelBox, edit=True, update=True)
