# object of MArrayLM class, part of the limma package, this array is very similar to a matrix however, this object has methods that may be separate.


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RModelFit import *
class RMArrayLM(RList):
    def __init__(self, data, parent = None, checkVal = True):
        RList.__init__(self, data = data, parent = parent, cm = cm, checkVal = False)
    
        #if self.getClass_data() != '
    def getIntercept_call(self):
        return self.data+'$Intercept'
    def getIntercept_data(self):
        return self.R(self.getIntercept_call(), silent = True, wantType = 'list')
    def copy(self):
        newData = RMArrayLM(data = self.data, parent = self.parent, cm = self.cm)
        newData.dictAttrs = self.dictAttrs
        return newData