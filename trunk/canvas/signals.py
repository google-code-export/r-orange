# Kyle R Covington
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RSession import Rcommand
from RSession import require_librarys
import glob,os.path,redREnviron

class BaseRedRVariable:# parent class of all signals.  This class holds base functions such as assignment and item setting
    def __init__(self, data, parent = None):
        
        self.data = data
        self.dictAttrs = {}
        self.reserved = ['data', 'dictAttrs']
        self.parent = parent
    def __getitem__(self, item):
        try:
            attr = getattr(self, item)
        except:
            try:
                attr = self.dictAttrs[item]
            except:
                attr = None
        return attr
    def saveSettings(self):
        return {'package': self.__package__, 'class':str(self.__class__), 'data':self.data, 'parent':self.parent, 'dictAttrs':self.dictAttrs}
        
    def loadSettings(self, settings):
        self.data = settings['data']
        self.parent = settings['parent']
        self.dictAttrs = settings['dictAttrs']
    def __setitem__(self, item, value):
        if item in self.reserved:
            raise Exception
        self.dictAttrs[item] = value
    def copyAllOptionalData(self,signal):
        import copy
        self.dictAttrs = copy.deepcopy(signal.dictAttrs)
    
    #(data, generator, comment, other)
    def setOptionalData(self, name, data, creatorWidget=None, description = None, extra=None):
        #if creatorWidget and type(creatorWidget) in [str]:
        widgetID = 'none'
        if hasattr(creatorWidget, 'widgetID'):
            widgetID = creatorWidget.widgetID
        
        if widgetID not in self.dictAttrs.keys():
            self.dictAttrs[widgetID] = {}
    
        self.dictAttrs[widgetID][name] = {'creator': widgetID, 
        'data':data,'description':description,'extra':extra}
    
    def getOptionalData(self,name):
        if name in self.dictAttrs:
            
            return self.dictAttrs[name]
        else:
            return None
    def optionalDataExists(self, name):
        if name in self.dictAttrs.keys():
            return True
        else:
            return False
    def __str__(self):
        ## print output for the class
        return 'Class: '+str(self.__class__)+'; Data: '+str(self.data)+'; Attributes: '+str(self.dictAttrs)
    def convertToClass(self, varClass):
        return self.copy()
    def keys(self):
        return self.dictAttrs.keys()
    def copy(self):
        import copy
        return copy.deepcopy(self)
    def removeOptionalData(self, data):
        self.dictAttrs.pop(data)
class RVariable(BaseRedRVariable): 
    def __init__(self, data, parent = None, checkVal = False):
        
        BaseRedRVariable.__init__(self,data)
        if not parent:
            parent = data
        self.parent = parent
        self.R = Rcommand
        self.require_librarys = require_librarys
        self.reserved = ['data', 'parent', 'R', 'dictAttrs']
    def __str__(self):
        ## print output for the class
        return '###Signal Class: '+str(self.__class__)+'; Data: '+self.data+'; Parent: '+self.parent+'; Attributes: '+str(self.dictAttrs)
    

    def getClass_call(self):
        return 'class('+self.data+')'
        
    def getClass_data(self):
        return self.R(self.getClass_call(), silent = True)

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
        print '|#|', item, subsetting
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

current_module = __import__(__name__)
RedRSignals = []
def registerRedRSignals(package):
    print '|#| registerRedRSignals for %s' % package
    import imp, sys
    # print sys.path
    m = imp.new_module(package)
    directory = os.path.join(redREnviron.widgetDir,package,'signalClasses')
    for filename in glob.iglob(os.path.join(directory,  "*.py")):
        # print 'import filename', filename
        if os.path.isdir(filename) or os.path.islink(filename):
            continue
        guiClass = os.path.basename(filename).split('.')[0]
        RedRSignals.append(guiClass)
        c = forname(guiClass,guiClass)
        c.__dict__['__package__'] = package
        setattr(m, guiClass,c)
    setattr(current_module,package,m)

for filename in glob.iglob(os.path.join(redREnviron.directoryNames['libraryDir'],'base','signalClasses',"*.py")):
    if os.path.isdir(filename) or os.path.islink(filename):
        continue
    signalClasses = os.path.basename(filename).split('.')[0]
    RedRSignals.append(signalClasses)
    c = forname(signalClasses,signalClasses)
    c.__dict__['__package__'] = 'base'
    setattr(current_module, signalClasses,c)


################Define global data###############

globalData = {}
def setGlobalData(creatorWidget, name, data, description = None, extra=None):
    if creatorWidget and type(creatorWidget) in [str]:
        widgetID = 'none'
    elif hasattr(creatorWidget, 'widgetID'):
        widgetID = creatorWidget.widgetID
        
    if widgetID not in globalData.keys():
        globalData[widgetID] = {}
    
    globalData[widgetID][name] = {'creator': widgetID, 
    'data':data,'description':description,'extra':extra}

def getGlobalData(name):
    for key,value in globalData.items():
        if name in value.keys(): 
            return value[name]
    
    return None
def globalDataExists(name):
    for key,value in globalData.items():
        if name in value.keys(): 
            return True
    
    return False
    
def removeGlobalData(data):
    del globalData[data]
