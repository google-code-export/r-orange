from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, glob
import redREnviron
from numpy import *
YesNo = NoYes = ("No", "Yes")
groupBoxMargin = 7

import os.path

        
enter_icon = None
class widgetState:
    def getDefaultState(self):
        r = {'enabled': self.isEnabled(),'hidden': self.isHidden()}
        return r
    def setDefaultState(self,data):
        # print ' in wdiget state'
        self.setEnabled(data['enabled'])
        self.setHidden(data['hidden'])
    def getSettings(self):
        pass
    def loadSettings(self,data):
        pass


def forname(modname, classname):
    ''' Returns a class of "classname" from module "modname". '''
    module = __import__(modname)
    classobj = getattr(module, classname)
    return classobj

qtWidgets = []
current_module = __import__(__name__)

def registerQTWidgets(package):
    print '@@@@@@@@@@registerQTWidgets'
    import imp
    m = imp.new_module(package)
    directory = os.path.join(redREnviron.directoryNames['widgetDir'],package,'qtWidgets')
    for filename in glob.iglob(os.path.join(directory,  "*.py")):
        if os.path.isdir(filename) or os.path.islink(filename):
            continue
        guiClass = os.path.basename(filename).split('.')[0]
        qtWidgets.append(guiClass)
        c = forname(guiClass,guiClass)
        c.__dict__['__package__'] = package
        setattr(m, guiClass,c)
    setattr(current_module,package,m)



for filename in glob.iglob(os.path.join(redREnviron.directoryNames['widgetDir'] + '/base/qtWidgets', "*.py")):
    if os.path.isdir(filename) or os.path.islink(filename):
        continue
    guiClass = os.path.basename(filename).split('.')[0]
    qtWidgets.append(guiClass)
    setattr(current_module, guiClass,forname(guiClass,guiClass))

    
    
def separator(widget, width=8, height=8):
    sep = QWidget(widget)
    if widget.layout(): widget.layout().addWidget(sep)
    sep.setFixedSize(width, height)
    return sep

    
def rubber(widget):
    widget.layout().addStretch(100)


#--------------------------------------------------------------------------------

