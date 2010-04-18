#  RvarClass for Generic Model Fit, inherits from list, other model fits should inherit from this class

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RList import *

class RModelFit(RList):
    def __init__(self, data, parent = None, checkVal = True):
        RList.__init__(self, data = data, parent = parent, checkVal = False)
        
    def _convertToModelFit(self):
        return self.copy()
    def _convertToList(self):
        newData = RList(data = 'as.list('+self.data+')', parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        return newData
    def copy(self):
        newVariable = RModelFit(data = self.data, parent = self.parent, cm = self.cm)
        newVariable.dictAttrs = self.dictAttrs
        return newVariable