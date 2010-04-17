from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RRectangularData import *

class RMatrix(RRectangularData):
    def __init__(self, data, parent = None, cm = None, checkVal = True):
        RRectangularData.__init__(self, data = data, parent = parent, cm = cm, checkVal = False)
        
        if cm: 
            print 'CM found'
            self.cm = cm
        else: # we only need to do this if a cm was not provided for us.
            ## This may raise an exception if the data is a subset of some other data (contains [] of $) widgets should only not send a cm if they are certain that a conversion will occur without probelms.
            rownames = self.R('rownames('+self.data+')')
            if rownames != None:
                self.R('cm_'+self.data+'<-data.frame(row.names = rownames('+self.data+'))')
            else:
                thisClass = self.R('class('+self.data+')')
                if thisClass not in ['data.frame', 'matrix', 'array']: # arrays are technically not allowed but there is the possibility of a two dimentional array that is not coerced to a matrix.
                    self.R('cm_'+self.data+'<-data.frame(row.names = make.names(rep(1:length('+self.data+'))))')
                else:
                    self.R('cm_'+self.data+'<-data.frame(row.names = make.names(rep(1:length('+self.data+'[1,]))))')
            self.cm = 'cm_'+self.data
            
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RRectangularData:
            return self._convertToRectangularData()
        else:
            raise Exception
    def _convertToRectangularData(self):
        return self.copy()
        
    def copy(self):
        newVariable = RMatrix(data = self.data, parent = self.parent, cm = self.cm)
        newVariable.dictAttrs = self.dictAttrs
        return newVariable
            