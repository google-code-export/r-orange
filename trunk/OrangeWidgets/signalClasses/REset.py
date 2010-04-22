# RAffybatch class, used to hold affybatch and eset objects.  Methods exist to convert to Rectangular Data, however, these methods rely on type conversion

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RMatrix import *

class REset(RList, RMatrix):
    def __init__(self, data, parent = None, checkVal = True):
        
        RMatrix.__init__(self, data = data, parent = parent, checkVal = False)
        
    def copy(self):
        newData = REset(data = self.data, parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        return newData
    def convertToClass(self, varClass):
        if varClass == RList:
            return self._convertToList()
        elif varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RDataFrame:
            return self._convertToDataFrame()
        elif varClass == RMatrix:
            return self._convertToMatrix()
        else:
            raise Exception, '%s Not A Defined Conversion Type' % str(varClass)
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
    def _convertToList(self):
        #self.R('list_of_'+self.data+'<-as.list('+self.data+')')
        newData = RList(data = 'as.list('+self.data+')', parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        newData.dictAttrs['eset'] = (self.data, 'RvarClass Conversion', 'Converted due to a copy to rectangular data', None)
        return newData