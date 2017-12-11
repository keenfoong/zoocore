zoocore
=========

Core python api for zootools

# Environment Variables
Zoo adds to the current environment, These variables accept multiple paths just make sure you create them before the
startup process.

- ZOO_BASE
- ZOO_ICON_PATH
- ZOO_META_PATHS
- ZOO_COMMAND_LIB

# Zoo Commands
Description
==============
Python command pattern with undo,redo functionality for standard applications and or DCCs if supported via command executors

Commands follow some strict rules.

- All commands must inherent from zoo.libs.command.command.ZooCommand
- All commands must have the following overrides
    - id(property) the command id
    - creator(property) the developer of the command name
    - isUndoable(property) Does the command support undo
    - doIt(method), Main method to do the operation
    - undoIt(method), if is undoable then undoIt() must be implemented

Commands provide persistent Gui data aka settings
These include :
    Label, icon, toolip, color(foreground), backgroundColor

Any command can have a QAction generate on demand via command.commandAction()

Usage
=====

The built command library lives under zoo.libs.command.library but users can add there own path via the environment
variable 'ZOO_COMMAND_LIB' then running the following

```python
from zoo.libs.command import executor
executor.Executor().registerEnv("ZOO_COMMAND_LIB")
```
To execute commands one must use the executor class and never execute the command directly otherwise
it will not be added to the internal undo stack and or the redostack.

``` python
# to execute a command
from zoo.libs.command import executor
exe = executor.Executor()
exe.executor("commandId", **kwargs)

```
To undo a command.

``` python
from zoo.libs.command import executor
executor.Executor().registerEnv("ZOO_COMMAND_LIB")
executor.undoLast()
```
To redo a command from the undostack.
``` python
from zoo.libs.command import executor
executor.Executor().registerEnv("ZOO_COMMAND_LIB")
executor.redoLast()
```

# ZOO QT
Zoo uses the follow third party wrapper.
https://github.com/mottosso/Qt.py.git

The location in zoo is expected to change to the thirdparty package under zoo but until then here's how you currently import it
```python
from zoo.libs.pyqt.qt import QtWidgets
```

Zoo.pyqt has a number of extensions to qt widgets, views and models.
