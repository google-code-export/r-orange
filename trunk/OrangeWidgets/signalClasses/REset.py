# RAffybatch class, used to hold affybatch and eset objects.  Methods exist to convert to Rectangular Data, however, these methods rely on type conversion

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RList import *
from RRectangularData import *
from RDataFrame import *
from RMatrix import *

class REset(RList, RRectangularData, RDataFrame, RMatrix):
    def __init__(self, data, parent = None, checkVal = True):
        RList.__init__(self, data = data, parent = parent, checkVal = False)
        RRectangularData.__init__(self, data = data, parent = parent, checkVal = False)
        RDataFrame.__init__(self, data = data, parent = parent, checkVal = False)
        RMatrix.__init__(self, data = data, parent = parent, checkVal = False)
        
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
        elif varClass == RDataFrame:
            return self._convertToDataFrame()
        elif varClass == RMatrix:
            return self._convertToMatrix()
        else:
            raise Exception
    def _convertToMatrix(self):
        newData = RMatrix(data = 'exprs('+self.data+')')
        newData.dictAttrs = self.dictAttrs
        newData.dictAttrs['eset'] = (self.data, 'RvarClass Conversion', 'Converted due to a conversion to rectangular data', None)
        return newData
    def _convertToDataFrame(self):
        newData = RRectangularData(data = 'as.data.frame(exprs('+self.data+'))')
        newData.dictAttrs = self.dictAttrs
        newData.dictAttrs['eset'] = (self.data, 'RvarClass Conversion', 'Converted due to a conversion to rectangular data', None)
        return newData
    def _convertToRectangularData(self):
        newData = RRectangularData(data = 'exprs('+self.data+')')
        newData.dictAttrs = self.dictAttrs
        newData.dictAttrs['eset'] = (self.data, 'RvarClass Conversion', 'Converted due to a conversion to rectangular data', None)
        return newData
    def _convertToList(self):
        #self.R('list_of_'+self.data+'<-as.list('+self.data+')')
        newData = RList(data = 'as.list('+self.data+')', parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        newData.dictAttrs['eset'] = (self.data, 'RvarClass Conversion', 'Converted due to a copy to rectangular data', None)
        return newData