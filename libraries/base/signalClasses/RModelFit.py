#  RvarClass for Generic Model Fit, inherits from list, other model fits should inherit from this class

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libraries.base.signalClasses.RList import *
from libraries.base.signalClasses.RVariable import *

class RModelFit(RList):
    convertToList = [RList, RVariable]
    def __init__(self, widget, data, parent = None, checkVal = True):
        RList.__init__(self, widget = widget, data = data, parent = parent, checkVal = False)
        self.RListSignal = None
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RModelFit:
            return self
        elif varClass == RList:
            return self._convertToList()
        else:
            raise Exception, '%s Not A Known Type' % unicode(varClass)
    def _convertToList(self):
        if not self.RListSignal:
            self.RListSignal = RList(data = 'as.list('+self.data+')') # we loose the parent at this point because of type conversion
            self.RListSignal.dictAttrs = self.dictAttrs.copy()
            return self.RListSignal
        else:
            return self.RListSignal
    # def copy(self):
        # newVariable = RModelFit(data = self.data, parent = self.parent)
        # newVariable.dictAttrs = self.dictAttrs.copy()
        # return newVariable