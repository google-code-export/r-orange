### Python Structured Dictionary Class.  Contains python dictionary objects and can be the parent class of other classes, even R classes.
### Dict must be a dictionary of lists and the lists must be of the same length.

from UnstructuredDict import *

class StructuredDict(UnstructuredDict):
    def __init__(self, data, parent = None, keys = None, checkVal = True):
        UnstructuredDict.__init__(self, data = data, parent = parent, keys = keys, checkVal = False)
        
        
        if checkVal:
            self.length = len(data[data.keys()[0]]) # the length of the first element
            if type(data) not in [dict]:
                raise Exception, 'Data not of dict type'
            
            for key in data.keys():
                if type(data[key]) not in [list]:
                    raise Exception, 'Data in '+str(key)+' not of list type'
                if len(data[key]) != self.length:
                    raise Exception, 'Data in '+str(key)+' not of same length as data in first key.'
                        
            if keys and len(keys) != len(self.data.keys()):
                print 'WARNING! Key length not same as keys.  Ignoring keys.'
                self.keys = self.data.keys()
            elif keys:
                self.keys = keys
            else:
                self.keys = self.data.keys()
        else:
            self.keys = None
            self.length = None
    def convertToClass(self, varClass):
        if varClass == BaseRedRVariable:
            return self
        elif varClass == UnstructuredDict:
            return self
        elif varClass == StructuredDict:
            return self
        else:
            raise Exception
            
    def getDims_data(self):
        return (len(self.data.keys()), self.length)