def rgbsToLinear(value):
    """Changes a single rgbs value (so say red only) and converts to linear

    :param value: a single color value, expects a value from 0-1
    :type value: float
    :return the new color value in linear
    :rtype float
    """
    a = 0.055  # I suppose this is the gamma
    return value * (1.0 / 12.92) if value <= 0.04045 else pow((value + a) * (1.0 / (1 + a)), 2.4)


def linearToRgbs(value):
    a = 0.055
    return value * 12.92 if value <= 0.0031308 else  (1 + a) * pow(value, 1 / 2.4) - a
