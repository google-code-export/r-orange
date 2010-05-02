# RAffybatch class, used to hold affybatch and eset objects.  Methods exist to convert to Rectangular Data, however, these methods rely on type conversion

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RMatrix import *
from RDataFrame import *

class REset(RMatrix):
    def __init__(self, data, parent = None, checkVal = True):
        
        RMatrix.__init__(self, data = data, parent = parent, checkVal = False)
        
    # def copy(self):
        # newData = REset(data = self.data, parent = self.parent)
        # newData.dictAttrs = self.dictAttrs.copy()
        # return newData
    def convertToClass(self, varClass):
        # if varClass == RList:
            # newData = self._convertToList()
        if varClass == RVariable:
            newData = self._convertToVariable()
        elif varClass == RDataFrame:
            newData = self._convertToDataFrame()
        elif varClass == RMatrix:
            newData = self._convertToMatrix()
        else:
            raise Exception, '%s Not A Defined Conversion Type' % str(varClass)
            
        newData.copyAllOptionalData(self)
        newData.setOptionalData(name='eset', data=self.data,creatorWidget=None,
        description='Converted due to a conversion to rectangular data')
        return newData
        
    def _convertToMatrix(self):
        newData = RMatrix(data = 'exprs('+self.data+')')
        return newData
    def _convertToDataFrame(self):
        newData = RDataFrame(data = 'as.data.frame(exprs('+self.data+'))')
        return newData
        
        