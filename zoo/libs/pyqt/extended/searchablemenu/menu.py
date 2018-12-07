"""Searchable QMenu

.. code-block:: python

    men = SearchableMenu(objectName="test", title="test menu")
    subMenu = men.addMenu("helloworld")
    act = taggedAction.TaggedAction("test")
    act.tags = set(["test", "hello", "world"])
    a = taggedAction.TaggedAction("bob")
    a.tags = set(["bob"])
    subMenu.addAction(act)
    men.addAction(a)
    men.exec_(QtGui.QCursor.pos())

"""
from qt import QtWidgets, QtGui, QtCore

from zoo.libs.pyqt.extended import menu
from zoo.libs.pyqt.extended.searchablemenu import action as taggedAction
from zoo.libs.pyqt import utils

__all__ = ("SearchableMenu",)


class SearchableMenu(menu.Menu):
    """ Extended the standard QMenu to make it searchable, first action is always a lineedit used to
    recursively search all sub actions by tags
    """

    mouseButtonClicked = QtCore.Signal(object)

    def __init__(self, **kwargs):
        """
        :param kwargs: Standard QMenu arguments
        :type kwargs: dict
        """
        super(SearchableMenu, self).__init__(**kwargs)
        self.setObjectName(kwargs.get("objectName"))
        self.setTitle(kwargs.get("title"))
        self._init()

    def _init(self):
        # search custom widget action
        self.searchAction = QtWidgets.QWidgetAction(self)
        self.searchAction.setObjectName("SearchAction")

        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setPlaceholderText("Search...")
        self.searchEdit.textChanged.connect(self.updateSearch)

        self.searchAction.setDefaultWidget(self.searchEdit)

        self.addAction(self.searchAction)
        self.addSeparator()

    def setSearchVisible(self, visible):
        """ Set visibility of the search edit

        :param visible:
        :return:
        """
        self.searchAction.setVisible(visible)

    def searchVisible(self):
        """ Returns visibility of search edit

        :return:
        """
        return self.searchAction.isVisible()

    def updateSearch(self, searchString=None):
        """Function that will search all actions for a search string tag

        :param searchString: tag names separated if a space eg. "my tag"
        :type searchString: str
        """
        searchString = searchString or ""
        tags = searchString.split()
        if not searchString:
            # if we don't have a valid string then all actions should be visible
            utils.recursivelySetActionVisiblity(self, True)
            return
        elif len(tags) > 1:
            _recursiveSearchByTags(self, tags)
            return
        _recursiveSearch(self, tags[0])


def _recursiveSearch(menu, searchString):
    for action in menu.actions():
        subMenu = action.menu()

        if subMenu:
            _recursiveSearch(subMenu, searchString)
            continue
        elif action.isSeparator():
            continue
        elif isinstance(action, taggedAction.TaggedAction) and not action.hasTag(searchString):
            action.setVisible(False)

    menuVis = any(action.isVisible() for action in menu.actions())
    menu.menuAction().setVisible(menuVis)


def _recursiveSearchByTags(menu, tags):
    for action in menu.actions():
        subMenu = action.menu()

        if subMenu:
            _recursiveSearchByTags(subMenu, tags)
            continue
        elif action.isSeparator():
            continue
        elif isinstance(action, taggedAction.TaggedAction):
            if action.hasAnyTag(tags):
                action.setVisible(True)
            else:
                action.setVisible(False)

    menuVis = any(action.isVisible() for action in menu.actions())
    menu.menuAction().setVisible(menuVis)
