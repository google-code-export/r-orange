## Sequence record object for the Biopython package

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from StructuredDict import *

class SequenceRecordCollection(StructuredDict):
    def __init__(self, data, parent = None, checkVal = True):
        StructuredDict.__init__(self, data = data, parent = parent, keys = data.keys(), checkVal = False)
        self.data = data  # place the data object into a holder, the data should be a collection of sequence records.
        self.keys = self.data.keys()
    
    def convertToClass(self, varClass):
        if varClass == BaseRedRVariable:
            return self
        elif varClass == SequenceRecordCollection:
            return self
        elif varClass == UnstructuredDict:
            return self._convertToStructuredDict()
        elif varClass == StructuredDict:
            return self._convertToStructuredDict()
        else:
            raise Exception, 'Can not convert to class '+str(varClass)
    def _convertToStructuredDict(self):
        newDict = {}
        newKeys = ['row_names', 'seq', 'id', 'name', 'description', 'letter_annotations', 'annotations', 'features', 'dbxrefs']
        for key in newKeys:
            newDict[key] = []
            
        for rec in self.data.keys(): ## move across all of the records
            record = self.data[rec]
            newDict['row_names'].append(rec)
            newDict['seq'].append(record.seq)
            newDict['id'].append(record.id)
            newDict['name'].append(record.name)
            newDict['description'].append(record.description)
            newDict['letter_annotations'].append(record.letter_annotations)
            newDict['annotations'].append(record.annotations)
            newDict['features'].append(record.features)
            newDict['dbxrefs'].append(record.dbxrefs)
        newData = StructuredDict(data = newDict, parent = self, keys = newKeys)
        return newData