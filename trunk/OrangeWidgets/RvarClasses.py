# Kyle R Covington
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RSession import Rcommand
import glob,os.path,orngEnviron

class BaseRedRVariable:
    def __init__(self, data):
        self.data = data
        self.dictAttrs = {}
        self.reserved = ['data', 'dictAttrs']
        
    def __getitem__(self, item):
        try:
            attr = getattr(self, item)
        except:
            try:
                attr = self.dictAttrs[item]
            except:
                attr = None
        return attr
    
    def __setitem__(self, item, value):
        if item in self.reserved:
            raise Exception
        self.dictAttrs[item] = value
    def __str__(self):
        ## print output for the class
        return 'Class: '+str(self.__class__)+'\nData: '+self.data+'\nAttributes: '+str(self.dictAttrs)
    def convertToClass(self, varClass):
        return self.copy()
    def keys(self):
        return self.dictAttrs.keys()
    def copy(self):
        newVariable = BaseRedRVariable(data = self.data)
        newVariable.dictAttrs = self.dictAttrs
        return newVariable

class RVariable(BaseRedRVariable): # parent class of all RvarClasses.  This class holds base functions such as assignment and item setting
    def __init__(self, data, parent = None, checkVal = False):
        # set the variables
        if not data:
            raise Exception()
        self.data = data
        if not parent:
            parent = data
        self.parent = parent
        self.dictAttrs = {}
        self.R = Rcommand
        self.reserved = ['data', 'parent', 'R', 'dictAttrs']
    def __getitem__(self, item):
        try:
            attr = getattr(self, item)
        except:
            try:
                attr = self.dictAttrs[item]
            except:
                attr = None
        return attr
    
    def __setitem__(self, item, value):
        if item in self.reserved:
            raise Exception
        self.dictAttrs[item] = value
    def __str__(self):
        ## print output for the class
        return 'Class: '+str(self.__class__)+'\nData: '+self.data+'\nParent: '+self.parent+'Attributes: '+str(self.dictAttrs)
    def keys(self):
        return self.dictAttrs.keys()
    def getClass_call(self):
        return 'class('+self.data+')'
        
    def getClass_data(self):
        return self.R(self.getClass_call(), silent = True)
        
    # def plotObject(self, dwidth=8, dheight=8, devNumber = 0, mfrow = None):
        # try:
            # query = 'plot('+self.data+')'
            # self.Rplot(query = query, dwidth = dwidth, dheight = dheight, devNumber = devNumber, mfrow = mfrow)
        # except:
            # print 'Exception occured'
    def saveSettings(self):
        return {'class':str(self.__class__), 'data':self.data, 'parent':self.parent, 'dictAttrs':self.dictAttrs}
        
    def loadSettings(self, settings):
        self.data = settings['data']
        self.parent = settings['parent']
        self.dictAttrs = settings['dictAttrs']
    def copy(self):
        newVariable = RVariable(self.data, self.parent)
        newVariable.dictAttrs = self.dictAttrs
        return newVariable
    def _simpleOutput(self, subsetting = ''):
        text = 'R Data Variable Name: '+self.data+'\n\n'
        return text
    def _fullOutput(self, subsetting = ''):
        text = self._simpleOutput()+'\n\n'
        text += 'R Data Variable Value: '+self.getAttrOutput_data(self.data, subsetting)+'\n\n'
        text += 'R Parent Variable Name: '+self.parent+'\n\n'
        text += 'R Parent Variable Value: '+self.getAttrOutput_data(self.parent, subsetting)+'\n\n'
        text += 'Class Dictionary: '+str(self.dictAttrs)+'\n\n'
        return text
    def getAttrOutput_call(self, item, subsetting = ''):
        print item, subsetting
        call = 'paste(capture.output('+self.__getitem__(item)+subsetting+'), collapse = "\n")'
        return call
    def getAttrOutput_data(self, item, subsetting = ''):
        return self.R(self.getAttrOutput_call(item = item, subsetting = subsetting))
    def getSimpleOutput(self, subsetting = ''):
        # return the text for a simple output of this variable
        text = 'Simple Output\n\n'
        text += 'Class: '+self.getClass_data()+'\n\n'
        text += self._simpleOutput(subsetting)
        return text
    def getFullOutput(self, subsetting = ''):
        text = 'Full Output\n\n'
        text += 'Class: '+self.getClass_data()+'\n\n'
        text += self._fullOutput(subsetting)
        return text
    def _convertToVariable(self):
        return self.copy()
    def convertToClass(self, varClass):
        return self.copy()
def forname(modname, classname):
    ''' Returns a class of "classname" from module "modname". '''
    module = __import__(modname)
    classobj = getattr(module, classname)
    return classobj

RVariableClasses = []
current_module = __import__(__name__)


for filename in glob.iglob(os.path.join(orngEnviron.directoryNames['widgetDir'] + '/signalClasses', "*.py")):
    if os.path.isdir(filename) or os.path.islink(filename):
        continue
    #print filename
    signalClasses = os.path.basename(filename).split('.')[0]
    RVariableClasses.append(signalClasses)
    setattr(current_module, signalClasses,forname(signalClasses,signalClasses))
