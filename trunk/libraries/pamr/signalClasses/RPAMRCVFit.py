from signals.RModelFit import RModelFit

class RPAMRCVFit(RModelFit):
    def __init__(self, data, checkVal = True):
        RModelFit.__init__(self, data = data, checkVal = False)
        
    def convertToClass(self, valClass):
        return self