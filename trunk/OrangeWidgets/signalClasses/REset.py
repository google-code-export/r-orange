# RAffybatch class, used to hold affybatch and eset objects.  Methods exist to convert to Rectangular Data, however, these methods rely on type conversion

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RList import *
from RRectangulrData import *

class REset(RList, RRectangulrData):
    def __init__(self, data, parent = None, checkVal = True):
        RList.__init__(self, data = data, parent = parent, checkVal = False)
        RRectangulrData.__init__(self, data = data, parent = parent, checkVal = False)
        
        self.dictAttrs['affybatch'] = self.data
    def copy(self):
        newData = REset(data = self.data, parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        return newData
    def convertToClass(self, varClass):
        if varClass == RList:
            return self._convertToList()
        elif varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RRectangularData:
            return self._convertToRectangularData()
        else:
            raise Exception
    def _convertToRectangularData(self):
        newData = RRectangularData(data = 'exprs('+self.data+')')
        newData.dictAttrs = self.dictAttrs
        newData.dictAttrs['eset'] = self.data
        return newData
    def _convertToList(self):
        #self.R('list_of_'+self.data+'<-as.list('+self.data+')')
        newData = RList(data = 'as.list('+self.data+')', parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        newData.dictAttrs['eset'] = self.data
        return newData