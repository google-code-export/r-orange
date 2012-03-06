## RArbitraryList signal, all list signals inherit from this

from libraries.base.signalClasses.RModelFit import *

## this model must be made by a caret model generator, no checking of value is possible.
class CaretModelFit(RModelFit):
    convertToList = [RVariable, UnstructuredDict, RArbitraryList, RModelFit]
    
    def __init__(self, widget, data, parent = None, checkVal = True, **kwargs):
        RModelFit.__init__(self, widget = widget, data = data, parent = parent, checkVal = False, **kwargs)
        
    def getClasses(self):
        return self.classes
        
    def convertToClass(self, varClass):
        if varClass in [CaretModelFit, RModelFit, RVariable, RArbitraryList]:
            return self
        else:
            return RModelFit.convertToClass(self, varClass)