# RAffybatch class, used to hold affybatch and eset objects.  Methods exist to convert to Rectangular Data, however, these methods rely on type conversion

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RMatrix import *
from RDataFrame import *

class REset(RMatrix):
    def __init__(self, data, parent = None, checkVal = True):
        
        RMatrix.__init__(self, data = data, parent = parent, checkVal = False)
        self.RMatrixSignal = None
        self.RDataFrameSignal = None
        self.RListSignal = None
        self.StructuredDictSignal = None
    def convertToClass(self, varClass):
        if varClass == RList:
            newData = self._convertToList()
        elif varClass == RVariable:
            return self
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
        
    def _convertToList(self):
        if not self.RListSignal:
            self.RListSignal = RList(data = 'as.list('+self.data+')')
            return self.RListSignal
        else:
            return self.RListSignal
    def _convertToMatrix(self):
        if not self.RMatrixSignal:
            self.RMatrixSignal = RMatrix(data = 'exprs('+self.data+')')
            self.RMatrixSignal.copyAllOptionalData(self)
            self.RMatrixSignal.setOptionalData(name='eset', data=self.data,creatorWidget=None,
            description='Converted due to a conversion to rectangular data')
            return self.RMatrixSignal
        else:
            return self.RMatrixSignal
    def _convertToDataFrame(self):
        if not self.RDataFrameSignal:
            self.RDataFrameSignal = RDataFrame(data = 'as.data.frame(exprs('+self.data+'))')
            self.RDataFrameSignal.copyAllOptionalData(self)
            self.RDataFrameSignal.setOptionalData(name='eset', data=self.data,creatorWidget=None,
            description='Converted due to a conversion to rectangular data')
            return self.RDataFrameSignal
        else:
            return self.RDataFrameSignal
        
        