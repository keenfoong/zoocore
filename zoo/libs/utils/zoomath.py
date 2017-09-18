import sys
import math

AXIS = {"x": 0,
        "y": 1,
        "z": 2}


def lerp(current, goal, weight=0.5):
    return (goal * weight) + ((1.0 - weight) * current)


def remap(value, oldMin, oldMax, newMin, newMax):
    return (((value - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin


def almostEqual(x, y, tailCount):
    return math.fabs(x - y) < sys.float_info.epsilon * math.fabs(x + y) * tailCount or math.fabs(
        x - y) < sys.float_info.min


def threePointParabola(a, b, c, iterations):
    positions = []
    for t in xrange(1, int(iterations)):
        x = t / iterations
        q = b + (b - a) * x
        r = c + (c - b) * x
        p = r + (r - q) * x
        positions.append(p)
    return positions
