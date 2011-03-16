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
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.qtWidgets.table import table
from libraries.base.qtWidgets.pyDataTable import pyDataTable as pyDataTable
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.lineEditHint import lineEditHint
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.tabWidget import tabWidget
import redRi18n
_ = redRi18n.get_(package = 'base')
class plateManipulator(OWRpy):
    
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["normPlate", "normList"])
        self.data = {}
        self.processedData = {}
        self.groupings = {}
        self.tables = {}
        self.inputs.addInput('plateData', 'Plate Data (must be numeric)', redRRMatrix, self.processData, multiple = True)
        self.outputs.addOutput('normPlate', 'Processed Values', redRRList)
        
        ## GUI
        
        box = widgetBox(self.controlArea, orientation = 'horizontal')
        tableBox = widgetBox(box)
        
        self.tableTabWidget = tabWidget(tableBox)
        
        rightBox = widgetBox(box)
        
        addBox = groupBox(rightBox, label = _('Selections'))
        self.groupEdit = lineEditHint(addBox, label = _('Group'))
        self.classEdit = lineEditHint(addBox, label = _('Class'))
        button(addBox, label = _('Add Selections To Model'), callback = self.addSelections)
        self.addBoxLable = widgetLabel(addBox, label = _('Add Box Label'), wordWrap = True)
        
        
        processBox = groupBox(rightBox, label = _('Prosess'))
        self.processSelect = comboBox(processBox, label = _('Process Method:'), items = ['Subtract', 'Divide', 'Add', 'Multiply'])
        self.acrossSelect = comboBox(processBox, label = _('Across:'))
        self.byGroupSelect = comboBox(processBox, label = _('By:'), callback = self.byGroupSelectChanged)
        self.bySubGroupSelect = comboBox(processBox, label = _('Control:'))
        self.methodSelect = comboBox(processBox, label = _('Combine Method:'), items = ['Average', 'Median', 'Max', 'Min'])
        self.constantEdit = lineEdit(processBox, label = _('Constant:'))
        button(processBox, label = _('Process'), callback = self.processAdjustment)
        #reshapeBox = groupBox(rightBox, label = _('Commit Data'))
        self.commit = redRCommitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction)
    def byGroupSelectChanged(self):
        self.bySubGroupSelect.update(['Constant'] + self.groupings[self.byGroupSelect.currentText()])
    def processAdjustment(self):
        ## this is how we are going to process the data
        ## reads as [Normalize] across [acrossSelect] by [byGroupSelect]:[Control] or Constant, this will perform Normalize across all levels of acrossSelect using those members that are labeled as [byGroupSelect]:[Control] as the right side of the equation, this happens across all tables and samples, no action is taken if no members of the acrossSelect group are also in the [byGroupSelect]:[Control] group.  For example, let's say there is a table like so 
        
            # a   b   c
        # 1   1   1   1   
        # 2   3   4   5
        # 3   7   8   9
        
        # let's further say that row 1 are all control listings of the "treatment" group, rows 2 and 3 are other treatment groups and the columns are "class" groups.  So if we wanted to say subtract the background of control from all classes our function would read Subtract across "class" by "treatment":"1"
        tempTables = {}
        for t in self.tables:
            newPlate = 'plateMod%s%s' % (t, str(self.processInt))
            self.processInt += 1  # index up the number of new plates
            self.setRvariableNames([newPlate])
            self.R('%s<-%s' % (self.Rvariables[newPlate], self.data[t]), wantType = 'NoConversion')
            tempTables[t] = self.Rvariables[newPlate]
        normlizeMethod = str(self.processSelect.currentText())
        acrossSelect = str(self.acrossSelect.currentText())
        byGroupSelect = str(self.byGroupSelect.currentText())
        control = str(self.bySubGroupSelect.currentText())
        combineMethod = str(self.methodSelect.currentText())
        for c in self.groupings[acrossSelect].keys():  ## c are the first set of groupings (a, b, and c from our example)
            controlLocs = [l for l in self.groupings[byGroupSelect][control] if l in self.groupings[acrossSelect][c]]
            if len(controlLocs) == 0: continue  ## continue because there are apparently no control locations to do anything with.
            controlVals = [float(self.R('data.matrix(%s)[%s,%s]' % (i[0], i[1]+1, i[2]+1))) for i in controlLocs] ## query R for the table, row and column for the values, note that the tables must be only numeric
            if combineMethod == 'Average':
                conVal = sum(controlVals)/len(controlVals)
            elif combineMethod == 'Median':
                if len(controlVals) % 2 == 1: ## an odd number
                    conVal = sorted(controlVals)[(len(controlVals)/2)]
                else:
                    conVal = (float(sorted(controlVals)[len(controlVals)/2]) + float(sorted(controlVals)[len(controlVals)/2 - 1]))/2.0
                    
            elif combineMethod == 'Min':
                conVal = min(controlVals)
            elif combineMethod == 'Max':
                conVal = max(controlVals)
            else:
                raise "Don't understand this combineMethod"
            
            if normlizeMethod == 'Subtract':
                for i in self.groupings[acrossSelect][c]:
                    self.R('%s[%s,%s]<-%s[%s, %s] - %s' % (tempTables[i[0]], i[1], i[2], i[0], i[1], i[2], conVal), wantType = 'NoConversion')
            elif normlizeMethod == 'Divide':
                for i in self.groupings[acrossSelect][c]:
                    self.R('%s[%s,%s]<-%s[%s, %s] / %s' % (tempTables[i[0]], i[1], i[2], i[0], i[1], i[2], conVal), wantType = 'NoConversion')
            elif normlizeMethod == 'Add':
                for i in self.groupings[acrossSelect][c]:
                    self.R('%s[%s,%s]<-%s[%s, %s] + %s' % (tempTables[i[0]], i[1], i[2], i[0], i[1], i[2], conVal), wantType = 'NoConversion')
            elif normlizeMethod == 'Multiply':
                for i in self.groupings[acrossSelect][c]:
                    self.R('%s[%s,%s]<-%s[%s, %s] * %s' % (tempTables[i[0]], i[1], i[2], i[0], i[1], i[2], conVal), wantType = 'NoConversion')
        for table in tempTables.values():
            self.processData(redRRDataFrame(self, data = 'as.data.frame(%s)' % table), table)
            
    def processData(self, data, id):
        if data:
            if id not in self.data.keys():
                page = self.tableTabWidget.createTabPage(str(id))
                self.tables[str(id)] = table(page, label = str(id), displayLabel = False, data = self.R('as.data.frame(%s)' % data.getData(), wantType = 'dict'))
            self.data[id] = data.getData()
            
                
        else:
            if id in self.data:
                self.tableTabWidget.removeTab(str(id))
                del self.data[id]
                
    def addGroupingData(self, gName):
        self.groupings[gName] = {}
        self.groupEdit.setItems(self.groupings.keys())
        self.acrossSelect.update(self.groupings.keys())
        self.byGroupSelect.update(self.groupings.keys())
    def removeGroupingData(self, gName):
        del self.groupings[gName]
        self.groupEdit.setItems(self.groupings.keys())
        self.acrossSelect.update(self.groupings.keys())
        self.byGroupSelect.update(self.groupings.keys())
    def addGroupingGroup(self, gName, group):
        self.groupings[gName][group] = []
        self.classEdit.setItems(self.groupings[gName].keys())
    def removeGroupingGroup(self, gName, group):
        del self.groupings[gName][group]
        self.classEdit.setItems(self.groupings[gName].keys())
    def appendValueTuple(self, gName, group, valueTuple):
        self.groupings[gName][group] += valueTuple
    def currentTable(self):
        return self.tableTabWidget.currentTab()
    ## adds selections to the data model, takes the group and class from the GUI
    def addSelections(self):
        if str(self.groupEdit.text()) not in self.groupings: self.addGroupingData(str(self.groupEdit.text()))
        if str(self.classEdit.text()) not in self.groupings[str(self.groupEdit.text())]: self.addGroupingGroup(str(self.classEdit.text()))
        
        ## convert selections to tuples
        tuples = [(self.data[self.currentTable()], i.row(), i.column()) for i in self.tables[self.currentTable()].selectedItems()]
        
        self.appendValueTuple(str(self.groupEdit.text()), str(self.classEdit.text()), tuples)
        self.addBoxLable.setText(_('Added selected items to %(GROUP)s, %(CLASS)s') % {'GROUP':str(self.groupEdit.text()), 'CLASS':str(self.classEdit.text())})
        
    def commitFunction(self):
        self.R('%s<-list(%s)' % (self.Rvariables['normList'], ','.join(self.data.values())))
        self.rSend('normPlate', redRRList(self, data = self.Rvariables['normList']))