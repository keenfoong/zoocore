from zoo.libs.command import command

from zoo.libs.maya.cameras import utils


class CreateCameraCommand(command.ZooCommand):
    """This command Create a standard camera and adds the node as a MetaCamera
    """
    id = "zoo.meta.camera.create"
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "camera",
              "tooltip": "Create camera",
              "label": "Create Camera",
              "color": "",
              "backgroundColor": ""
              }
    _meta = None

    def resolveArguments(self, arguments):
        name = arguments.get("name")
        if not name:
            self.cancel("Please provide a name")

        return arguments

    def doIt(self, name=None, start=0, end=1, focalLength=35.000, horizontalFilmAperture=1.682):
        self._meta = utils.createCamera(name, start, end, focalLength, horizontalFilmAperture)
        return self._meta

    def undoIt(self):
        if self._meta is not None and self._meta.exists():
            self._meta.delete()
            return True
        return False