from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, glob 
import redREnviron
import redRExceptionHandling
import os.path
import imp
        
class widgetState:
    def __init__(self,widgetName,includeInReports,**args):
        #print args
        # if 'alignment' in args.keys():
            # parent.layout().setAlignment(self,args['alignment'])
        self.includeInReports=includeInReports
        if not widgetName:
            print '#########widget Name is required############'
            
            # try:
            raise RuntimeError('#########widget Name is required############')
            # except:
                # print redRExceptionHandling.formatException()

        self.widgetName = widgetName
    
    def getReportText(self,fileDir):
        # print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        # print 'self', self, self.widgetName
        children = self.children()
        # print children
        if len(children) ==0:
            return False
            
        reportData = {}
        for i in children:
            if isinstance(i, widgetState):
                d = i.getReportText(fileDir)
                if type(d) is dict:
                    reportData.update(d)
                # dd = []
                # if type(d) is dict:
                    # for x in d.items():
                        # x['includeInReports'] = i.includeInReports
                        # dd.append(x)
                    # reportData = reportData + dd
                # elif d:
                    # d['includeInReports'] = i.includeInReports
                    # reportData.append(d)
        
        return reportData

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


# def forname(modname, classname):
    # ''' Returns a class of "classname" from module "modname". '''
    # module = __import__(modname)
    # classobj = getattr(module, classname)
    # return classobj

# current_module = __import__(__name__)
qtWidgets = []

def registerQTWidgets():   
    for package in os.listdir(redREnviron.directoryNames['libraryDir']): 
        if not (os.path.isdir(os.path.join(redREnviron.directoryNames['libraryDir'], package)) 
        and os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'))):
            continue
        try:
            directory = os.path.join(redREnviron.directoryNames['libraryDir'],package,'qtWidgets')
            for filename in glob.iglob(os.path.join(directory,  "*.py")):
                if os.path.isdir(filename) or os.path.islink(filename):
                    continue
                guiClass = os.path.basename(filename).split('.')[0]
                qtWidgets.append(guiClass)
        except:
           print redRExceptionHandling.formatException()


# def separator(widget, width=8, height=8):
    # sep = QWidget(widget)
    # if widget.layout(): widget.layout().addWidget(sep)
    # sep.setFixedSize(width, height)
    # return sep

    
# def rubber(widget):
    # widget.layout().addStretch(100)
