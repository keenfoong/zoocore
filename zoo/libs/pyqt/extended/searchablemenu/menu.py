"""Searchable QMenu

::example:
    >>> men = SearchableMenu(objectName="test", title="test menu")
    >>> subMenu = men.addMenu("helloworld")
    >>> act = taggedAction.TaggedAction("test")
    >>> act.tags = set(["test", "hello", "world"])
    >>> a = taggedAction.TaggedAction("bob")
    >>> a.tags = set(["bob"])
    >>> subMenu.addAction(act)
    >>> men.addAction(a)
    >>> men.exec_(QtGui.QCursor.pos())

"""
from qt import QtWidgets

from zoo.libs.pyqt.extended.searchablemenu import action as taggedAction
from zoo.libs.pyqt import utils

__all__ = ("SearchableMenu",)


class SearchableMenu(QtWidgets.QMenu):
    """Extended the standard QMenu to make it searchable, first action is always a lineedit used to
    recursively search all sub actions by tags
    """

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
        searchAction = QtWidgets.QWidgetAction(self)
        searchAction.setObjectName("SearchAction")

        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setPlaceholderText("Search...")
        self.searchEdit.textChanged.connect(self.updateSearch)

        searchAction.setDefaultWidget(self.searchEdit)

        self.addAction(searchAction)
        self.addSeparator()

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
            print action, tags, action.tags, "multi", action.hasAnyTag(tags)

    menuVis = any(action.isVisible() for action in menu.actions())
    menu.menuAction().setVisible(menuVis)