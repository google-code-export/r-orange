from RModelFit import *

class RROCPerformanceFit(RModelFit):
    def __init__(self, data, parent = None, checkVal = True):
        RModelFit.__init__(self, data = data, parent = parent, checkVal = False)
        self.RListSignal = None
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RModelFit:
            return self
        elif varClass == RROCPerformanceFit:
            return self
        elif varClass == RList:
            return self._convertToList():
        else:
            raise Exception, '%s Not A Known Type' % str(varClass)
    def _convertToList(self):
        if not self.RListSignal:
            self.RListSignal = RList(data = 'as.list('+self.data+')') # we loose the parent at this point because of type conversion
            self.RListSignal.dictAttrs = self.dictAttrs.copy()
            return self.RListSignal
        else:
            return self.RListSignal
