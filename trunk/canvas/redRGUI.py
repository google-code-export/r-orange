from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, glob 
import redREnviron

import os.path
import imp
import redRi18n
import redRLog

_ = redRi18n.Coreget_()
class qtWidgetBox(QWidget):
    def __init__(self,widget):
        QWidget.__init__(self,widget)
        if widget and widget.layout() not in [0,None]:
            widget.layout().addWidget(self)
        #if widget and widget.layout() not in [0,None]: 
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setMargin(0)
        self.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

       
class widgetState:
    def __init__(self,widget,widgetName,includeInReports,**kwargs):
        if not widgetName:
            raise RuntimeError(_('#########widget Name is required############'))
        self.controlArea = qtWidgetBox(widget)
        if hasattr(self,'getReportText'):
            self.controlArea.getReportText = self.getReportText
        else:
            self.controlArea.getReportText = self.getReportTextDefault
        
        self.includeInReports=includeInReports
        
        if not widgetName:
            raise RuntimeError(_('#########widget Name is required############'))

        self.widgetName = widgetName
        
        if 'toolTip' in kwargs:
            self.controlArea.setToolTip(kwargs['toolTip'])
        if 'sizePolicy' in kwargs:
            self.controlArea.setSizePolicy(kwargs['sizePolicy'])
        if 'whatsThis' in kwargs:
            self.controlArea.setWhatsThis(kwargs['whatsThis'])
        elif 'toolTip' in kwargs:
            self.controlArea.setWhatsThis(kwargs['toolTip'])
        if 'disabled' in kwargs:
            self.controlArea.setDisabled(kwargs['disabled'])
        if 'styleSheet' in kwargs:
            self.controlArea.setStyleSheet(kwargs['styleSheet'])
    def hide(self):
        self.controlArea.hide()
    
    def show(self):
        self.controlArea.show()
    def isVisible(self):
        return self.controlArea.isVisible()
    def isEnabled(self):
        return self.controlArea.isEnabled()
    def setDisabled(self,e):
        self.controlArea.setDisabled(e)
    def setEnabled(self,e):
        self.controlArea.setEnabled(e)
    def isEnabled(self):
        return self.controlArea.isEnabled()
    def getReportTextDefault(self,fileDir):
        # print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        # print _('self'), self, self.widgetName
        children = self.children()
        # print children
        if len(children) ==0:
            return False
            
        reportData = {}
        for i in children:
            if isinstance(i, qtWidgetBox):
                d = i.getReportText(fileDir)
                if type(d) is dict:
                    reportData.update(d)
        
        return reportData
    def deleteWidget(self):
        """Call the deleteWidget function in all of the child widgets, this will remove or undo any concequences of the widgets actions.
        
        All child widgets that reimplement this function should, at a minimum, do the following;
        
        children = self.children()
        if len(children) == 0: return
        for i in children:
            if isinstance(i, qtWidgetBox):
                i.deleteWidget()
                
        This can be achieved by calling widgetState.deletWidget(self).
        """
        children = self.children()
        if len(children) == 0: return
        for i in children:
            if isinstance(i, qtWidgetBox):
                i.deleteWidget()
                
    def getDefaultState(self):
        r = {'enabled': self.controlArea.isEnabled(),'hidden': self.controlArea.isHidden()}
        return r
    def setDefaultState(self,data):
        # print _(' in wdiget state')
        
        self.controlArea.setEnabled(data.get('enabled', True))
        self.controlArea.setHidden(data.get('hidden', False))
    def getSettings(self):
        pass
    def loadSettings(self,data):
        pass
    
    def layout(self):
        return self.controlArea.layout()
    def setEnabled(self,b):
        self.controlArea.setEnabled(b)
        
    def safeLoad(self, data, name, default = None):
        try:
            return data[name]
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.WARNING, 'Error loading setting for %s, defaulting to %s' % (name, default))
            return default


def forname(modname, classname):
    ''' Returns a class of "classname" from module "modname". '''
    #print modname
    module = __import__(modname, globals(), locals(),classname)
    #print module
    classobj = getattr(module, classname)
    return classobj

qtWidgets = []
current_module = __import__(__name__)
def registerQTWidgets():   
    for package in os.listdir(redREnviron.directoryNames['libraryDir']): 
        if not (os.path.isdir(os.path.join(redREnviron.directoryNames['libraryDir'], package)) 
        and os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'))):
            continue
        
        m = imp.new_module(package)
        directory = os.path.join(redREnviron.directoryNames['libraryDir'],package,'qtWidgets')
        for filename in glob.iglob(os.path.join(directory,  "*.py")):
            if os.path.isdir(filename) or os.path.islink(filename) or os.path.split(filename)[1] == '__init__.py':
                continue
            try:    
                guiClass = os.path.basename(filename).split('.')[0]
                qtWidgets.append(guiClass)
                
                c = forname('libraries.%s.qtWidgets.%s' % (package,guiClass),guiClass)
                setattr(m, guiClass, c)
            except:
               redRLog.log(redRLog.REDRCORE, redRLog.WARNING,redRLog.formatException())
        setattr(current_module,package,m)
            
#registerQTWidgets()
