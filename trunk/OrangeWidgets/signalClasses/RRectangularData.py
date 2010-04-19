# Abstract rectangular data class RRectangularData, base class for objects such as data.frame and matrix
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RvarClasses import RVariable

class RRectangularData(RVariable):
    def __init__(self, data, cm = None, parent = None, checkVal = True):
        RVariable.__init__(self, data = data, parent = parent, checkVal = False)
        #if checkVal and self.getClass_data() != 'data.frame':
            #raise Exception # there this isn't the right kind of data for me to get !!!!!
        self.cm = cm
        self.reserved.append('cm')
    def copy(self):
        newVariable = RRectangularData(self.data, self.parent, self.cm)
        newVariable.dictAttrs = self.dictAttrs
        return newVariable
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        else:
            raise Exception
    def _convertToVariable(self):
        # newData = RVariable(data = self.data, parent = self.parent)
        # newData.dictAttrs = self.dictAttrs
        # newData.dictAttrs['cm'] = self.cm
        return self.copy()