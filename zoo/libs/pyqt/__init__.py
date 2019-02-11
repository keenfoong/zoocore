import os

from zoo.libs.pyqt import stylesheet

# load the zoo fonts
fontPath = os.path.join(os.path.dirname(__file__), "fonts")
stylesheet.loadFonts([os.path.join(fontPath, fontFile) for fontFile in os.listdir(fontPath)])