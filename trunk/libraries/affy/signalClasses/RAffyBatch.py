from signals import RVariable
class RAffyBatch(RVariable):

    def __init__(self, data):
        RVariable.__init__(self, data = data)

    def convertToClass(self, varClass):
        if varClass == RVariable:
            return self
        else:
            raise Exception
