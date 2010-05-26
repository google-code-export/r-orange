from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RList import *
from StructuredDict import *


class RDataFrame(RList, StructuredDict):
    def __init__(self, data, parent = None, checkVal = True):
        StructuredDict.__init__(self, data = data, parent = parent, checkVal = False)
        RList.__init__(self, data = data, parent = parent, checkVal = False)
        if checkVal and self.getClass_data() != 'data.frame':
            raise Exception('not a dataframe') # there this isn't the right kind of data for me to get !!!!!
        self.RListSignal = None
        self.structuredDict = None
    def convertToClass(self, varClass):
        if varClass == RList:
            return self._convertToList()
        elif varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RDataFrame:
            return self
        elif issubclass(StructuredDict, varClass):
            return self._convertToStructuredDict()
        else:
            raise Exception
    def _convertToStructuredDict(self):
        if not self.structuredDict:
            dictData = self.R(self.data, wantType = 'dict', silent = False)
            dictData['row_names'] = self.R('rownames('+self.data+')', wantType = 'list')
            keys = ['row_names']
            keys += self.R('colnames('+self.data+')')
            self.structuredDict = StructuredDict(data = dictData, parent = self, keys = keys)
            return self.structuredDict
        else:
            return self.structuredDict
    def _convertToList(self):
        if not self.RListSignal:
            #self.R('list_of_'+self.data+'<-as.list('+self.data+')')
            self.RListSignal = RList(data = 'as.list('+self.data+')', parent = self.parent)
            self.RListSignal.dictAttrs = self.dictAttrs.copy()
            return self.RListSignal
        else:
            return self.RListSignal
    def getSimpleOutput(self, subsetting = '[1:5, 1:5]'):
        # return the text for a simple output of this variable
        text = 'Simple Output\n\n'
        text += 'Class: '+self.getClass_data()+'\n\n'
        text += self._simpleOutput(subsetting)
        return text
    def _fullOutput(self, subsetting = ''):
        text = self._simpleOutput()+'\n\n'
        text += 'R Data Variable Value: '+self.getAttrOutput_data('data', subsetting)+'\n\n'
        dims = self.getDims_data()
        text += 'R Data Variable Size: '+str(dims[0])+' Rows and '+str(dims[1])+' Columns\n\n'
        text += 'R Parent Variable Name: '+self.parent+'\n\n'
        text += 'R Parent Variable Value: '+self.getAttrOutput_data('parent', subsetting)+'\n\n'
        text += 'Class Dictionary: '+str(self.dictAttrs)+'\n\n'
        return text
    def getRownames_call(self):
        return 'rownames('+self.data+')'
    def getRownames_data(self):
        return self.R(self.getRownames_call(), wantType = 'list', silent = True)
    def getItem_call(self, item):
        if type(item) in [int, float, long]:
            item = int(item)
            return self.data+'[,'+str(item)+']'
        elif type(item) in [str]:
            return self.data+'[,\''+str(item)+'\']'
        elif type(item) in [list]:
            newItemList = []
            for i in item:
                if type(i) in [int, float, long]:
                    newItemList.append(str(int(i)))
                elif type(i) in [str]:
                    newItemList.append('\"'+str(i)+'\"')
            return self.data+'[,c('+str(newItemList)[1:-1]+')]'
        else:
            return self.data #just return all of the data and hope the widget picks up from there
    def getItem_data(self, item, wantType = 'dict'): # native functionality is to return a dict (this is what lists do)
        call = self.getItem_call(item)
        if call != None:
            if type(item) in [int, str, long, float]:
                return self.R(call, wantType = wantType, silent = True) # returns a single column
            elif type(item) in [list] and wantType not in ['array', 'list']: # returns a dict
                return self.R(call, wantType = wantType, silent = True)
                
            elif type(item) in [list] and wantType in  ['array', 'list']: # returns a list of lists
                return self.R('as.matrix('+call+')', wantType = wantType, silent = True)
        else:
            print 'No data to return'
            return {}
    def getColumnnames_call(self):
        return self.getNames_call()
    def getColumnnames_data(self):
        return self.getNames_data()
    def getRange_call(self, rowRange = None, colRange = None):
        if rowRange == None and colRange == None:
            return self.data
        if rowRange:
            rr = str(rowRange)
        else:
            rr = ''
        if colRange:
            cr = str(colRange)
        else:
            cr = ''
        return self.data+'['+rr+','+cr+']'
    def getRowData_call(self, item):
        if type(item) in [int, float, long]:
            item = int(item)
            return self.data+'['+str(item)+',]'
        elif type(item) in [str]:
            return self.data+'[\''+str(item)+'\',]'
        elif type(item) in [list]:
            newItemList = []
            for i in item:
                if type(i) in [int, float, long]:
                    newItemList.append(str(int(i)))
                elif type(i) in [str]:
                    newItemList.append('\"'+str(i)+'\"')
            return self.data+'[c('+str(newItemList)[1:-1]+'),]'
        else:
            return self.data #just return all of the data and hope the widget picks up from there
    def getRowData_data(self, item):
        output = self.R(self.getRowData_call(item), wantType = 'list', silent = True)
        return output