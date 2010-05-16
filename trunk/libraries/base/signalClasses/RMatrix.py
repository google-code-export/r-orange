from RDataFrame import *

class RMatrix(RDataFrame):
    def __init__(self, data, parent = None, checkVal = True):
        RDataFrame.__init__(self, data = data, parent = parent, checkVal = False)
        if checkVal and self.getClass_data() != 'matrix':
            raise Exception('not a Matrix.') # there this isn't the right kind of data for me to get !!!!!


    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RDataFrame:
            return self._convertToRDataFrame()
        elif varClass == RList:
            return self._convertToRList()
        else:
            raise Exception
    def _convertToRDataFrame(self):
        newData = RDataFrame(data = 'as.data.frame('+self.data+')', parent = self.parent)
        newData.dictAttrs = self.dictAttrs.copy()
        return newData
    def _convertToRList(self):
        newData = RList(data = 'as.list(as.data.frame('+self.data+'))')
        newData.dictAttrs = self. dictAttrs.copy()
        return newData
    # def copy(self):
        # newVariable = RMatrix(data = self.data, parent = self.parent)
        # newVariable.dictAttrs = self.dictAttrs.copy()
        # return newVariable
            