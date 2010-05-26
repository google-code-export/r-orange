from RDataFrame import *

class RMatrix(RDataFrame):
    def __init__(self, data, parent = None, checkVal = True):
        RDataFrame.__init__(self, data = data, parent = parent, checkVal = False)
        if checkVal and self.getClass_data() != 'matrix':
            raise Exception('not a Matrix.') # there this isn't the right kind of data for me to get !!!!!

        self.RDataFrameSignal = None
        self.RListSignal = None
        self.StructuredDictSignal = None

    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RDataFrame:
            return self._convertToRDataFrame()
        elif varClass == RList:
            return self._convertToRList()
        elif varClass == RMatrix:
            return self
        elif varClass == StructuredDict:
            return self._convertToStructuredDict()
        elif varClass == UnstructuredDict:
            return self._convertToStructuredDict()
        else:
            raise Exception
    def _convertToStructuredDict(self):
        if not self.StructuredDictSignal:
            data = self.R('as.data.frame('+self.data+')', wantType = 'dict')
            keys = ['row_names']
            keys += self.R('colnames(as.data.frame('+self.data+'))', wantType = 'list')
            rownames = self.R('rownames('+self.data+')', wantType = 'list')
            if rownames[0] in [None, 'NULL', 'NA']:
                rownames = [str(i+1) for i in range(len(data[data.keys()[0]]))]
            data['row_names'] = rownames
            self.StructuredDictSignal = StructuredDict(data = data, parent = self, keys = keys)
            return self.StructuredDictSignal
        else:
            return self.StructuredDictSignal
    def _convertToRDataFrame(self):
        if not self.RDataFrameSignal:
            self.RDataFrameSignal = RDataFrame(data = 'as.data.frame('+self.data+')', parent = self.parent)
            self.RDataFrameSignal.dictAttrs = self.dictAttrs.copy()
            return self.RDataFrameSignal
        else:
            return self.RDataFrameSignal
    def _convertToRList(self):
        if not self.RListSignal:
            self.RListSignal = RList(data = 'as.list(as.data.frame('+self.data+'))')
            self.RListSignal.dictAttrs = self. dictAttrs.copy()
            return self.RListSignal
        else:
            return self.RListSignal
            