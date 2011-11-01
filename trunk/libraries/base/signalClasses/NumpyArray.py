"""Numpy Array Signal
helpdoc::
This signal class provides interfaces for numpy arrays.  Numpy is inclued with Red-R and these arrays are ubiquitously used within many Python toolkits.  Arrays are similar to matrices and can be interconverted.
"""
from signals import BaseRedRVariable
import numpy as np
"""
.. convertTo:: ``
.. convertFrom:: ``
"""
class NumpyArray(BaseRedRVariable):
    convertToList = [BaseRedRVariable]
    convertFromList = []
    def __init__(self, widget, data, parent = None, checkVal = False, **kwargs):
        BaseRedRVariable.__init__(self, widget = widget, data = data, parent = parent, checkVal = False)
        
        if checkVal:
            if type(data) not in [np.ndarray]:
                raise Exception, 'Data not of  class'
    def getData(self):
        return self.data
    def convertToClass(self, varClass):
        if varClass == BaseRedRVariable:
            return self
        else:
            raise Exception
