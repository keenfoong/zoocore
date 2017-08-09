from maya.api import OpenMayaAnim as om2Anim
from maya.api import OpenMaya as om2


def setCurrentRange(start, end, newCurrentFrame):
    """Set's maya's frame range and the current time number.

    :param start: The start of the frame range to set
    :type start: int
    :param end: The end of the frame range to set
    :type end: int
    :param newCurrentFrame: The frame number to set maya's current time to.
    :type newCurrentFrame: ints
    """
    currentUnit = om2Anim.MAnimControl.currentTime().unit
    start = om2.MTime(start, currentUnit)
    end = om2.MTime(end, currentUnit)
    newTime = om2.MTime(newCurrentFrame, currentUnit)
    om2Anim.MAnimControl.setMinMaxTime(start, end)
    om2Anim.MAnimControl.setAnimationStartEndTime(start, end)
    om2Anim.MAnimControl.setCurrentTime(newTime)
