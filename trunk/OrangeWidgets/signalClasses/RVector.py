from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RSession import Rcommand
from RMatrix import *
class RVector(RMatrix):
    def __init__(self, data, parent = None, checkVal = True):
        RMatrix.__init__(self, data = data, parent = parent, checkVal = False)
    def copy(self):
        newVariable = RVector(data = self.data, parent = self.parent)
        newVariable.dictAttrs = self.dictAttrs
        return newVariable
    def convertToClass(self, varClass):
        if varClass == RList:
            return self._convertToList()
        elif varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RDataFrame:
            return self._convertToDataFrame()
        elif varClass == RMatrix():
            return self._convertToMatrix()
        elif varClass == RVector:
            return self.copy()
        else:
            raise Exception
    def _convertToMatrix(self):
        newData = RMatrix(data = 'as.matrix('+self.data+')')
        newData.dictAttrs = self.dictAttrs
        return newData
    def _convertToList(self):
        self.R('list_of_'+self.data+'<-as.list(as.data.frame('+self.data+'))')
        newData = RList(data = 'list_of_'+self.data, parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        return newData
    def _convertToRectangularData(self):
        return self._convertToDataFrame()
    def _convertToDataFrame(self):
        # self.R('data_frame_of_'+self.data+'<-as.data.frame('+self.data+')')
        # self.R('colnames(data_frame_of_'+self.data+')<-c(\''+self.data+'\')')
        newData = RDataFrame(data = 'as.data.frame('+self.data+')', parent = self.parent)
        newData.dictAttrs = self.dictAttrs
        return newData
        
    def _convertToVariable(self):
        return self.copy()
        
    def getSimpleOutput(self, subsetting = '[1:5]'):
        # return the text for a simple output of this variable
        text = 'Simple Output\n\n'
        text += 'Class: '+self.getClass_data()+'\n\n'
        text += self._simpleOutput(subsetting)
        return text
    
    def getColumnnames_call(self):
        return self.getNames_call()
    def getColumnnames_data(self):
        return self.getNames_data()
    def getNames_call(self):
        return self.data
    def getNames_data(self):
        return self.data # the only name to speek of the name of the variable

    def getRange_call(self, rowRange = None, colRange = None):
        if rowRange == None: return self.data
        else: return self.data+'['+str(rowRange)+']'
        
        