## RLme4ModelFit; a model fit for lme4 models made use lmer.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from RModelFit import *

class RLme4ModelFit(RModelFit):
    def __init__(self, data, parent, checkVal = True):
        RModelFit.__init__(self, data = data, parent = parent, checkVal = False)
        ## we require a parent that can be checked using the lmerAnova funciton
        self.RListSignal = None
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        elif varClass == RModelFit:
            return self
        elif varClass == RLme4ModelFit:
            return self
        else:
            raise Exception, '%s Not A Known Type' % str(varClass)
    def _convertToModelFit(self):
        return self
    def _convertToList(self):
        if not self.RListSignal:
            self.RListSignal = RList(data = 'as.list('+self.data+')') # we loose the parent at this point because of type conversion
            self.RListSignal.dictAttrs = self.dictAttrs.copy()
            return self.RListSignal
        else:
            return self.RListSignal