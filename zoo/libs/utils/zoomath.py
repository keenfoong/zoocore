import sys
import math


def lerp(current, goal, weight=0.5):
    return (goal * weight) + ((1.0 - weight) * current)


def remap(value, oldMin, oldMax, newMin, newMax):
    return (((value - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin;


def almostEqual(x, y, tailCount):
    return math.fabs(x - y) < sys.float_info.epsilon * math.fabs(x + y) * tailCount or math.fabs(
        x - y) < sys.float_info.min
