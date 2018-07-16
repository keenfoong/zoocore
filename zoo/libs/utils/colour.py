"""Colors

This module contains functions related to color but not specific to any particular softawre
"""

import colorsys
from math import radians, sqrt, cos, sin


def convertHsvToRgb(hsv):
    """Converts hsv values to rgb
    rgb is in 0-1 range, hsv is in (0-360, 0-1, 0-1) ranges

    :param hsv: Hue Saturation Value Hue is in 0-360 range, Sat/Value 0-1 range
    :type hsv: list
    :return rgb: Red Green Blue values 0-1
    :rtype rgb: list
    """
    rgb = list(colorsys.hsv_to_rgb((hsv[0] / 360.0), hsv[1], hsv[2]))  # convert HSV to RGB
    return rgb


def convertRgbToHsv(rgb):
    """Converts rgb values to hsv
    rgb is in 0-1 range, hsv is in (0-360, 0-1, 0-1) ranges

    :return hsv: Red Green Blue values 0-1
    :rtype hsv: list
    :param rgb: Hue Saturation Value Hue is in 0-360 range, Sat/Value 0-1 range
    :type rgb: list
    """
    hsv = list(colorsys.rgb_to_hsv((rgb[0]), rgb[1], rgb[2]))
    hsv[0] *= 360.0
    return hsv


def convertSingleSrgbToLinear(colorValue):
    """Changes a single rgb color (so say red only) to linear space

    :param colorValue: a single color value, expects a value from 0-1
    :type colorValue: float
    :return Linear: the new color converted to linear
    :rtype Linear: float
    """
    a = 0.055
    if colorValue <= 0.04045:
        return colorValue * (1.0 / 12.92)
    return pow((colorValue + a) * (1.0 / (1 + a)), 2.4)


def convertSingleLinearToSrgb(colorValue):
    """Changes a single rgb color (so say red only) in linear so the resulting color is displayed
    in srgb color space

    :param colorValue: a single color value, expects a value from 0-1
    :type colorValue: float
    :return Srgb: the new color converted to srgb
    :rtype Srgb: float
    """
    a = 0.055
    if colorValue <= 0.0031308:
        return colorValue * 12.92
    return (1 + a) * pow(colorValue, 1 / 2.4) - a


def convertColorSrgbToLinear(srgbColor):
    """Changes a srgb color to linear color

    :param srgbColor: a rgb color list/tuple, expects values from 0-1
    :type srgbColor: list of floats
    :return linearRgb: the new color gamma convered to linear
    :rtype linearRgb: float
    """
    return (convertSingleSrgbToLinear(srgbColor[0]),
            convertSingleSrgbToLinear(srgbColor[1]),
            convertSingleSrgbToLinear(srgbColor[2]))


def convertColorLinearToSrgb(linearRgb):
    """Changes a linear color to srgb color

    :param linearRgb: a rgb color list/tuple, expects values from 0-1
    :type linearRgb: list of floats
    :return the new color gamma converted to srgb
    :rtype tuple(float)
    """
    return (convertSingleLinearToSrgb(linearRgb[0]),
            convertSingleLinearToSrgb(linearRgb[1]),
            convertSingleLinearToSrgb(linearRgb[2]))


def convertSrgbListToLinear(srgbList, roundNumber=True):
    """Converts a list to linear, optional round to 4 decimal places

    :param srgbList: list of srgb colors range 0-1 eg (0.0, 1.0, 0.0)
    :type srgbList: list
    :param roundNumber: do you want to round to 4 decimal places?
    :type roundNumber: bool
    :return linearRgbList: The list of colors converted to linear color
    :rtype linearRgbList: list
    """
    linearRgbList = list()
    for col in srgbList:
        linColorLong = convertColorSrgbToLinear(col)
        if roundNumber:
            linCol = list()
            for longNumber in linColorLong:
                roundedNumber = round(longNumber, 4)
                linCol.append(roundedNumber)
            linearRgbList.append(linCol)
        else:
            linearRgbList.append(linColorLong)
    return linearRgbList


def offsetHueColor(hsv, offset):
    """Offsets the hue value (0-360) by the given `offset` amount
    keeps in range 0-360 by looping
    Max offset is 360, min is -360

    :param hsv: The hue sat val color list [180, .5, .5]
    :type hsv: list
    :param offset: How much to offset the hue component, can go past 360 or less than 0. 0-360 color wheel
    :type offset: float
    :return hsv: The new hsv list eg [200, .5, .5]
    :rtype hsv: list
    """
    if offset > 360:
        offset = 360
    elif offset < -360:
        offset = -360
    hsv[0] += offset
    # reset value so it lies within the 0-360 range
    if hsv[0] > 360:
        hsv[0] -= 360
    elif hsv[0] < 0:
        hsv[0] += 360
    return hsv


def offsetSaturation(hsv, offset):
    """Offsets the "saturation" value (0-1) by the given `offset` amount
    keeps in range 0-1 by looping

    :param hsv: a 3 value list or tuple representing a the hue saturation and value color [180, .5, .5]
    :type hsv: list
    :param offset: the offset value to offset the color
    :type offset: float
    :return hsv: the hue saturation value color eg [200, .5, .5]
    :rtype: list
    """
    hsv[1] += offset
    # reset value so it lies within the 0-360 range
    if hsv[1] > 1:
        hsv[1] = 1
    elif hsv[1] < 0:
        hsv[1] = 0
    return hsv


def offsetColor(col, offset=0):
    """Returns a color with the offset in tuple form.

    :param col: Color in form of tuple with 3 ints. eg tuple(255,255,255)
    :type col: tuple(int,int,int)
    :param offset: The int to offset the color
    :return: tuple (int,int,int)
    """
    return tuple([clamp(c+offset) for c in col])


def offsetValue(hsv, offset):
    """Offsets the "value" (brightness/darkness) value (0-1) by the given `offset` amount
    keeps in range 0-1 by looping

    :param hsv: a 3 value list or tuple representing a the hue saturation and value color [180, .5, .5]
    :type hsv: list
    :param offset: the offset value to offset the color
    :type offset: float
    :return hsv: the hue saturation value color eg [200, .5, .5]
    :rtype: list
    """
    hsv[2] += offset
    # reset value so it lies within the 0-360 range
    if hsv[2] > 1:
        hsv[2] = 1
    elif hsv[2] < 0:
        hsv[2] = 0
    return hsv


def hueShift(col, shift):
    """Shifts the hue of the given colour

    :param col: Colour to shift
    :type col: tuple(int,int,int)
    :param shift: The distance and direction of the colour to shift
    :type shift: int
    :return:
    """
    rgbRotator = RGBRotate()
    rgbRotator.set_hue_rotation(shift)
    return rgbRotator.apply(*col)


def clamp(v):
    if v < 0:
        return 0
    if v > 255:
        return 255
    return int(v + 0.5)


class RGBRotate(object):
    """Hue Rotation, using the matrix rotation method. From here

    https://stackoverflow.com/questions/8507885/shift-hue-of-an-rgb-color
    """
    def __init__(self):
        self.matrix = [[1,0,0],[0,1,0],[0,0,1]]

    def set_hue_rotation(self, degrees):
        cosA = cos(radians(degrees))
        sinA = sin(radians(degrees))
        self.matrix[0][0] = cosA + (1.0 - cosA) / 3.0
        self.matrix[0][1] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
        self.matrix[0][2] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
        self.matrix[1][0] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
        self.matrix[1][1] = cosA + 1./3.*(1.0 - cosA)
        self.matrix[1][2] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
        self.matrix[2][0] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
        self.matrix[2][1] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
        self.matrix[2][2] = cosA + 1./3. * (1.0 - cosA)

    def apply(self, r, g, b):
        rx = r * self.matrix[0][0] + g * self.matrix[0][1] + b * self.matrix[0][2]
        gx = r * self.matrix[1][0] + g * self.matrix[1][1] + b * self.matrix[1][2]
        bx = r * self.matrix[2][0] + g * self.matrix[2][1] + b * self.matrix[2][2]
        return clamp(rx), clamp(gx), clamp(bx)
