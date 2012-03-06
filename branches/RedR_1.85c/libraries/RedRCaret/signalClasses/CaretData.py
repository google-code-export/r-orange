## RArbitraryList signal, all list signals inherit from this

from libraries.base.signalClasses.RArbitraryList import *
from libraries.base.signalClasses.RDataFrame import *

class CaretData(RArbitraryList):
    convertFromList = [UnstructuredDict, StructuredDict]
    convertToList = [RVariable, UnstructuredDict, RDataFrame]
    
    def __init__(self, widget, data, classes = '', parent = None, checkVal = True, **kwargs):
        RArbitraryList.__init__(self, widget = widget, data = data, parent = parent, checkVal = False, **kwargs)
        if checkVal and self.getClass_data() not in ['data.frame', 'matrix', 'preProcess']:
            raise Exception
        self.classes = classes
    ## returns a dict of settings used to reset the signal class on loading.
    def saveSettings(self):
        return {'class':unicode(self.__class__), 'data':self.data, 'parent':self.parent, 'dictAttrs':self.dictAttrs, 'classes':self.classes}
        
    ## sets the signal data from a dict returned by saveSettings
    def loadSettings(self, settings):
        self.data = settings['data']
        self.parent = settings['parent']
        self.dictAttrs = settings['dictAttrs']
        self.classes = settings['classes']
    def getClasses(self):
        return self.classes
        
    def convertFromClass(self, signal):
        return RArbitraryList.convertFromClass(self, signal)
        
    def convertToClass(self, varClass):
        if varClass == CaretData:
            return self
        elif varClass == RDataFrame:
            return RDataFrame(self.widget, data = 'as.data.frame('+self.getData()+')')
        else:
            return RArbitraryList.convertToClass(self, varClass)