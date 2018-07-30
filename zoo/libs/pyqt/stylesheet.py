import os
from qt import QtGui

class StyleSheet(object):
    """

    .. code-block:: python

        styleSheetStr = "QToolTip{background - color: rgb(BACK_COLOR_R, BACK_COLOR_G, BACK_COLOR_B);color: black;border: blacksolid 1px;margins: 2px;}"
        settings = {"BACK_COLOR_R": 251, "BACK_COLOR_G": 15, "BACK_COLOR_B": 10}
        sheet = StyleSheet(styleSheetStr)
        sheet.format(settings)
        print sheet.data
        # result
        QToolTip {
            background-color: rgb(251, 15, 10);
            color: black;
            border: black solid 1px;
            margins: 2px;
        }

    """

    @classmethod
    def fromPath(cls, path, **kwargs):
        """

        :param path: The style stylesheet css file
        :type path: str
        :param kwargs: The settings to replace in the style sheet
        :type kwargs: dict
        :rtype: :class:`StyleSheet`
        """

        with open(path, "r") as f:
            styleSheet = cls(f.read())
        if kwargs:
            styleSheet.format(kwargs)
        return styleSheet

    def __init__(self, styleSheet=None):
        self.data = styleSheet or ""
        self.originaldata = str(styleSheet)

    def __repr__(self):
        return str(self.data)

    def format(self, settings):
        """Formats the stylesheet str with the settings

        :param settings: A dict containing the str to replace and the value to replace with eg. {"BACK_COLOR_R": 251}
        :type settings: dict
        :return: True if successfully formatted
        :rtype: bool
        """
        if not self.data:
            return False
        data = str(self.data)
        for key, value in settings.items():
            data = data.replace(key, str(value))
        self.data = data
        return True


def stylesheetFromDirectory(directory, name):
    """Recursively searches directory until the name.css file is found and a :class:`Stylesheet` instance is returned

    :param directory: The absolute path to the directory to search
    :type directory: str
    :param name: the file name to find
    :type name: str
    :return: The style sheet instance or None if no matching file is found
    :rtype: tuple(:class:`StyleSheet`, str)
    """
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".css") and f.startswith(name):
                path = os.path.join(root, f)
                return StyleSheet.fromPath(path), path


def stylesheetsFromDirectory(directory):
    """Recursively searches the directory for all .css files and returns :class:`StyleSheet` instances and file paths

    :param directory: The absolute path to the directory to search
    :type directory: str
    :return:
    :rtype: list(tuple(:class:`StyleSheet`, str))
    """
    sheets = list()
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".css"):
                path = os.path.join(root, f)
                sheets.append((StyleSheet.fromPath(path), path))
    return sheets

def loadFonts(fontPaths):
    """Load's the given '.ttf' font files into the QtGui.QFontDatabase

    :param fontPaths: A list of font files
    :type fontPaths: list(str)
    :return: the list of registered font ids from qt
    :rtype: list(str)
    """
    return [QtGui.QFontDatabase.addApplicationFont(font) for font in fontPaths]

