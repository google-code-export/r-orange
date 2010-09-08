## commitButton (just like button but with a fancy icon)

from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libraries.base.qtWidgets.button import button
import redREnviron
class commitButton(button,widgetState):
    def __init__(self,widget,label, callback = None, disabled=0, icon=None, 
    toolTip=None, width = None, height = None,align='left', toggleButton = False, addToLayout = 1):
        button.__init__(self, widget = widget, label = label, callback = callback, disabled = disabled, icon = str(redREnviron.directoryNames['libraryDir']+'/base/icons/fork.png').replace('\\', '/'), toolTip = toolTip, width = width, height = height, align = align, toggleButton = toggleButton, addToLayout = addToLayout)
        self.setIcon(QIcon(str(redREnviron.directoryNames['libraryDir']+'/base/icons/fork.png').replace('\\', '/')))
        print self.icon(), 'Icon'
        