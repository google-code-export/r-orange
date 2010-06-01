## RNeuralNet

from RModelFit import *

class RNeuralNet(RModelFit):
    def convertToClass(varClass):
        if varClass == RNeuralNet:
            return self
        else:
            return RModelFit.convertToClass(varClass)