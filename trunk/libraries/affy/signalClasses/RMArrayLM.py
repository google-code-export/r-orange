# object of MArrayLM class, part of the limma package, this array is very similar to a matrix however, this object has methods that may be separate.


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RModelFit import *
class RMArrayLM(RModelFit):
    def __init__(self, data, parent = None, checkVal = True):
        RModelFit.__init__(self, data = data, parent = parent, checkVal = False)
        self.RListSignal = None
        #if self.getClass_data() != '
    def getIntercept_call(self):
        return self.data+'$Intercept'
    def getIntercept_data(self):
        return self.R(self.getIntercept_call(), silent = True, wantType = 'list')
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RModelFit:
            return self
        elif varClass == RList:
            return self._convertToList()
        elif varClass == RMArrayLM:
            return self
        else:
            raise Exception
    # def copy(self):
        # newData = RMArrayLM(data = self.data, parent = self.parent)
        # newData.dictAttrs = self.dictAttrs.copy()
        # return newData
    def _convertToList(self):
        if not self.RListSignal:
            self.RListSignal = RList(data = 'as.list('+self.data+')') # we loose the parent at this point because of type conversion
            self.RListSignal.dictAttrs = self.dictAttrs.copy()
            return self.RListSignal
        else:
            return self.RListSignal