from signals.RList import RList

class RPAMRData(RList):
    def __init__(self, data, checkVal = True):
        RList.__init__(self, data = data, checkVal = False)
        
    def convertToClass(self, valClass):
        return self