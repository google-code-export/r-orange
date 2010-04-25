from RvarClasses import RVariable
class RAffyBatch(RVariable):

    def __init__(self, data):
        RVariable.__init__(self, data = data)
    def copy(self):
        newVariable = RAffyBatch(self.data)
        newVariable.dictAttrs = self.dictAttrs.copy()
        return newVariable
    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self._convertToVariable()
        else:
            raise Exception
