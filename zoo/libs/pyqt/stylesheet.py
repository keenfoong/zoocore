class StyleSheet(object):
    """
    ::example:
        >>> styleSheetStr = 'QToolTip { \n\tbackground-color: rgb(BACK_COLOR_R, BACK_COLOR_G, BACK_COLOR_B);\n\tcolor: black;\n\tborder: black solid 1px;\n\tmargins: 2px;\n}\n'
        >>> settings = {"BACK_COLOR_R": 251,
                    "BACK_COLOR_G": 15,
                    "BACK_COLOR_B": 10}

        >>> sheet = stylesheet.StyleSheet(styleSheetStr)
        >>> sheet.format(settings)
        >>> print sheet.data
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
        :rtype: ::class:`StyleSheet`
        """

        with open(path, "r") as f:
            styleSheet = cls(f.readLines())
        styleSheet.format(**kwargs)
        return styleSheet

    def __init__(self, styleSheet=None):
        self.data = styleSheet or ""
        self.originaldata = str(styleSheet)

    def __repr__(self):
        return self.data

    def format(self, settings):
        if not self.data:
            return False
        data = str(self.data)
        for key, value in settings.items():
            data = data.replace(key, str(value))
        self.data = data
        return True
