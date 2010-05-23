# Kyle R Covington
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import glob,os.path,redREnviron



# parent class of all signals.  This class holds base functions such as assignment and item setting
class BaseRedRVariable:
    def __init__(self, data, parent = None, checkVal = False):
        
        self.data = data
        self.dictAttrs = {}
        self.reserved = ['data', 'dictAttrs']
        self.parent = parent
    
    def getData(self):
        return self.data

    def getDataParent(self):
        return self.parent

    def getItem(self, name):
        ## gets a required item from the signal, this does not query the dictAttrs but could return it.
        try:
            attr = getattr(self, name)
            return attr
        except:
            return None
    def saveSettings(self):
        return {'package': self.__package__, 'class':str(self.__class__), 'data':self.data, 'parent':self.parent, 'dictAttrs':self.dictAttrs}
        
    def loadSettings(self, settings):
        self.data = settings['data']
        self.parent = settings['parent']
        self.dictAttrs = settings['dictAttrs']
    def copyAllOptionalData(self,signal):
        import copy
        self.dictAttrs = copy.deepcopy(signal.dictAttrs)
    
    #(data, generator, comment, other)
    def setOptionalData(self, name, data, creatorWidget=None, description = None, extra=None):
        #if creatorWidget and type(creatorWidget) in [str]:
        widgetID = 'none'
        if hasattr(creatorWidget, 'widgetID'):
            widgetID = creatorWidget.widgetID
        else:
            widgetID = None
    
        self.dictAttrs[name] = {'creator': widgetID, 
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
        string = 'Class: '+str(self.__class__)+'; Data: '+str(self.data)
        
        return string
    def convertToClass(self, varClass):
        return self.copy()
    def keys(self):
        return self.dictAttrs.keys()
    def copy(self):
        import copy
        return copy.deepcopy(self)
    def removeOptionalData(self, name):
        del self.dictAttrs['name']
    def deleteSignal(self):
        print 'Deleting signal'
        


##############################################################

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
    
def forname(modname, classname):
    ''' Returns a class of "classname" from module "modname". '''
    module = __import__(modname)
    classobj = getattr(module, classname)
    return classobj
          
################Run on Init###############


current_module = __import__(__name__)
RedRSignals = []

for filename in glob.iglob(os.path.join(redREnviron.directoryNames['libraryDir'],'base','signalClasses',"*.py")):
    if os.path.isdir(filename) or os.path.islink(filename):
        continue
    signalClasses = os.path.basename(filename).split('.')[0]
    RedRSignals.append(signalClasses)
    c = forname(signalClasses,signalClasses)
    c.__dict__['__package__'] = 'base'
    setattr(current_module, signalClasses,c)


