from zoo.libs.command import executor
from zoo.libs.maya.markingmenu import menu
from maya import cmds


class Layout(menu):
    executor = executor.Executor()

    def validate(self, layout=None):
        layout = layout or self.data
        failed = []
        for item, data in layout:
            if isinstance(data, Layout):
                failed.extend(self.validate(data))
            elif item == "generic":
                failed.extend(self._validateGeneric(data))
            command = self.executor.findCommand(data)
            if not command:
                failed.append(data)
        return failed

    def _validateGeneric(self, data):
        failed = []
        for item in data:
            if isinstance(item, basestring):
                command = self.executor.findCommand(item)
                if not command:
                    failed.append(item)
                continue
            elif isinstance(item, dict):
                failed.extend(self._validateGeneric(item["generic"]))
        return failed


class MarkingMenu(menu.MarkingMenu):
    def __init__(self, layout, name, parent, commandExecutor):
        super(MarkingMenu, self).__init__(layout, name, parent)
        self.commandExecutor = commandExecutor

    def _buildGeneric(self, data, menu, parent):
        for item in data:
            if isinstance(item, basestring):
                command = self.commandExecutor.findCommand(item)
                uiData = command.uiData
                uiData.create(parent=menu)
                uiData.triggered.connect(self.commandExecutor.execute)
                continue
            elif item["type"] == "menu":
                subMenu = cmds.menuItem(label=item["label"], subMenu=True)
                self._buildGeneric(item["children"], subMenu, parent)

    def show(self, layout, menu, parent):
        for item, data in layout.items():
            if not data:
                continue
            # menu generic menu
            if item == "generic":
                self._buildGeneric(data, menu, parent)
                continue
            # nested marking menu
            elif isinstance(data, Layout):
                radMenu = cmds.menuItem(label=data["id"], subMenu=True, radialPosition=item.upper())
                self.show(data, radMenu, parent)
                continue
            # single item
            command = self.commandExecutor.findCommand(data)
            uiData = command.uiData
            uiData.create(parent=menu)
            cmds.menuItem(uiData.item, e=True, radialPosition=item.upper())
            uiData.triggered.connect(self.commandExecutor.execute)
