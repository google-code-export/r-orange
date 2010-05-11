## Sequence record object for the Biopython package

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from BaseRedRVariable import *


class SequenceRecordCollection(BaseRedRVariable):
    def __init__(self, data, parent = None, checkVal = True):
        self.data = data  # place the data object into a holder, the data should be a collection of sequence records.