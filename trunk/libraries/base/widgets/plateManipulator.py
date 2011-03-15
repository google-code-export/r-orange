## plateManipulator, a tool to work with plates of any size.  This tool will do some of the basic leg work for you for example, normalize a series of plates to some background value, or normalize a series of measurements to a control value for relative induction.

"""
<name>Plate Manipulator</name>
<tags>Data Input</tags>
<icon>readfile.png</icon>
"""

import redRGUI
from OWRpy import *
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.UnstructuredDict import UnstructuredDict
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix
from libraries.base.qtWidgets.table import table
from libraries.base.qtWidgets.pyDataTable import pyDataTable as pyDataTable
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.lineEdit import lineEdit
import redRi18n
_ = redRi18n.get_(package = 'base')
class plateManipulator(OWRpy):
    
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["normPlate"])
        self.data = {}
        self.processedData = {}
        self.inputs.addInput('plateData', 'Plate Data (must be numeric)', redRRMatrix, self.processData, multiple = True)
        self.outputs.addOutput('normPlate', 'Processed Values', redRRMatrix)
        
        ## GUI
        
        
    def processData(self, data, id):
        if data:
            self.data[id] = data.getData()
        else:
            if id in self.data:
                del self.data[id]
                
    def addGroupingData(self, gName):
        self.groupings[gName] = {}
    def removeGroupingData(self, gName):
        del self.groupings[gName]
    def addGroupingGroup(self, gName, group, valueTuple):
        self.groupings[gName][group] = valueTuple
    def removeGroupingGroup(self, gName, group):
        del self.groupings[gName][group]
                