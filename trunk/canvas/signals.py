from PyQt4.QtCore import *
from PyQt4.QtGui import *
import glob,os.path,redREnviron
import imp, sys
import redRLog
# import redRi18n
def _(a):
    return a
# _ = redRi18n.Coreget_()

# parent class of all signals.  This class holds base functions such as assignment and item setting
class BaseRedRVariable:
    ## init function, requires; 
        #widget - parent widget of the signal class, if a derived signal then pass the parent widget to that signal, all signals are ultimately owned by a widget
        #data - any python object can be considered data in this class, will be assigned to self.data
    ## init function optionals;
        #parent - parent of the current data, used if the signal data is derived from a larger data structure, implement in modules
        #checkVal - check that the value sent as data is of the appropriate type, implemented in child classes.
    def __init__(self, widget, data, parent = None, checkVal = False):
        
        self.data = data
        self.dictAttrs = {}
        self.reserved = ['data', 'dictAttrs']
        self.parent = parent
        self.widget = widget
    ## returns the current data object in self.data
    def getData(self):
        return self.data
           
   ## returns the current data object in self.parent
    def getDataParent(self):
        return self.parent
        
    ## returns a dict of settings used to reset the signal class on loading.
    def saveSettings(self):
        return {'class':unicode(self.__class__), 'data':self.data, 'parent':self.parent, 'dictAttrs':self.dictAttrs}
        
    ## sets the signal data from a dict returned by saveSettings
    def loadSettings(self, settings):
        self.data = settings['data']
        self.parent = settings['parent']
        self.dictAttrs = settings['dictAttrs']
    
    ## sets the dictAttrs of this signal to those of another signal
    def copyAllOptionalData(self,signal):
        import copy
        self.dictAttrs = copy.deepcopy(signal.dictAttrs)
    
    ## sets some optional data from this signal, typically used in a package to coordinate extra data that may be tangential to a signal
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
    
    ## returns a dict of settings set by the setOptionalData function; creator, data, description, extra
    def getOptionalData(self,name):
        if name in self.dictAttrs:
            
            return self.dictAttrs[name]
        else:
            return None
    
    ## check if an optional data slot exists, returns bool 
    def optionalDataExists(self, name):
        if name in self.dictAttrs.keys():
            return True
        else:
            return False
            
    ## removes optional data from the signal class
    def removeOptionalData(self, name):
        del self.dictAttrs[name]
        
    ## returns a string representing the current data
    def __str__(self):
        ## print output for the class
        string = 'Class: '+unicode(self.__class__)+'; Data: '+unicode(self.data)
        
        return string
        
    ## returns a summary representing the current data; defaults to returning the string
    def summary(self):
        return self.__str__()
    
    ## return a signal class of the desired type modified in such a way as to conform to the new signal types rules; reimplement in child classes
    def convertToClass(self, varClass):
        return self.copy()
    
    ## returns the keys of the dictAttrs
    def keys(self):
        return self.dictAttrs.keys()
        
    ## returns a copy of self that is independent
    def copy(self):
        import copy
        return copy.deepcopy(self)
        
    
    ## deletes the signal, reimplement if your signal if you need consequences.
    def deleteSignal(self):
        pass
        print _('Deleting signal')
        
    ## generates a progress bar and returns it
    def progressBar(self, title = _('Signal Prosess'), text = '', max = 100):
        progressBar = QProgressDialog()
        progressBar.setCancelButtonText(QString())
        progressBar.setWindowTitle(title)
        progressBar.setLabelText(text)
        progressBar.setMaximum(max)
        progressBar.setValue(0)
        progressBar.show()
        return progressBar


##############################################################

def registerRedRSignals():
    for package in os.listdir(redREnviron.directoryNames['libraryDir']): 
        if not (os.path.isdir(os.path.join(redREnviron.directoryNames['libraryDir'], package)) 
        and os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'],package,'package.xml'))):
            continue
        
        m = imp.new_module(package)
        directory = os.path.join(redREnviron.directoryNames['libraryDir'],package,'signalClasses')
        if not os.path.isdir(directory): continue
        
        for filename in glob.iglob(os.path.join(directory,  "*.py")):
            # print _('import filename'), filename
            if os.path.isdir(filename) or os.path.islink(filename) or os.path.split(filename)[1] == '__init__.py':
                continue
            try:
                signalClass = os.path.basename(filename).split('.')[0]  ## the signal object filename
                RedRSignals.append(signalClass) ## append the object filename to the RedRSignals list
                c = forname('libraries.%s.signalClasses.%s' % (package,signalClass),signalClass)
                #c.__dict__['__package__'] = package
                setattr(m, signalClass,c)
            except:
                redRLog.log(redRLog.REDRCORE, redRLog.WARNING,redRLog.formatException())
        setattr(current_module,package,m)

def setRedRSignalModule(modname, mod): # to be called on init of each signalClass package __init__

    ## goal is to eventually run setattr(current_module, --packageName--, --someModule--)
    setattr(current_module, modname, mod)
def forname(modname, classname):
    ''' Returns a class of "classname" from module "modname". '''
    module = __import__(modname, globals(), locals(),classname)
    classobj = getattr(module, classname)
    return classobj
          
################Run on Init###############


current_module = __import__(__name__)
RedRSignals = []

# import libraries.base.signalClasses.RVariable 
# import libraries.base.signalClasses.RVector

# for filename in glob.iglob(os.path.join(redREnviron.directoryNames['libraryDir'],'base','signalClasses',"*.py")):
    # if os.path.isdir(filename) or os.path.islink(filename):
        # continue
    # try:
        # signalClasses = os.path.basename(filename).split('.')[0]
        # RedRSignals.append(signalClasses)
        # c = forname(signalClasses,signalClasses)
        # setattr(c,'__package__','base')
        # setattr(current_module, signalClasses,c)
    # except Exception as inst:
        # print inst
#registerRedRSignals()
