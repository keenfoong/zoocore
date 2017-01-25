"""This is the main zoo package, we split code into sub package by context, if the code is tool dependent
it goes in zoo.apps else zoo.libs, DCC dependent libs go zoo.libs.DCCType  eg. zoo.libs.maya
"""
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

MAJOR_VERSION = 0
MINOR_VERSION = 1
PATCH_VERSION = 0

version = ".".join([str(MAJOR_VERSION), str(MINOR_VERSION), str(PATCH_VERSION)])
__version__ = version
