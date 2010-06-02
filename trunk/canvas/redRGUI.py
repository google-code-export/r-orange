from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, glob, orngOutput
import redREnviron
from numpy import *
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
    # print '@@@@@@@@@@registerQTWidgets'
    import imp
    m = imp.new_module(package)
    directory = os.path.join(redREnviron.directoryNames['libraryDir'],package,'qtWidgets')
    for filename in glob.iglob(os.path.join(directory,  "*.py")):
        if os.path.isdir(filename) or os.path.islink(filename):
            continue
        guiClass = os.path.basename(filename).split('.')[0]
        qtWidgets.append(guiClass)
        c = forname(guiClass,guiClass)
        # print c, 'forname return'
        # print package, 'package return'
        setattr(c,'__package__',package)
        #c.__dict__['__package__'] = package
        setattr(m, guiClass,c)
    setattr(current_module,package,m)


for filename in glob.iglob(os.path.join(redREnviron.directoryNames['libraryDir'] + '/base/qtWidgets', "*.py")):
    if os.path.isdir(filename) or os.path.islink(filename):
        continue
    guiClass = os.path.basename(filename).split('.')[0]
    qtWidgets.append(guiClass)
    c = forname(guiClass,guiClass)
    setattr(c,'__package__','base')
    setattr(current_module, guiClass,c)

for package in os.listdir(redREnviron.directoryNames['libraryDir']): 
    if (os.path.isdir(os.path.join(redREnviron.directoryNames['libraryDir'], package)) 
    and os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'))):
        try:
            registerQTWidgets(package)
        except:
            orngOutput.printException()    
    
def separator(widget, width=8, height=8):
    sep = QWidget(widget)
    if widget.layout(): widget.layout().addWidget(sep)
    sep.setFixedSize(width, height)
    return sep

    
def rubber(widget):
    widget.layout().addStretch(100)


#--------------------------------------------------------------------------------

