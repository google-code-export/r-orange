from RModelFit import *

class RROCPerformanceFit(RModelFit):
    def __init__(self, data, parent = None, checkVal = True):
        RModelFit.__init__(self, data = data, parent = parent, checkVal = False)
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RModelFit:
            return self.copy()
        elif varClass == RROCPerformanceFit:
            return self.copy()
        else:
            raise Exception, '%s Not A Known Type' % str(varClass)
    def _convertToModelFit(self):
        return self.copy()
    def _convertToList(self):
        newData = RList(data = 'as.list('+self.data+')') # we loose the parent at this point because of type conversion
        newData.dictAttrs = self.dictAttrs.copy()
        return newData
    def copy(self):
        newVariable = RROCPerformanceFit(data = self.data, parent = self.parent)
        newVariable.dictAttrs = self.dictAttrs.copy()
        return newVariable