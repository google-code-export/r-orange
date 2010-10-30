"""
<name>Set Operations</name>
<tags>Data Manipulation</tags>
<icon>datatable.png</icon>
"""

from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RList import RList as redRRList

from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.textEdit import textEdit



class setOperations(OWRpy): 
    globalSettingsList = ['commitOnInput']

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["intersect"])
        self.dataA = None
        self.dataB = None
        
        self.inputs.addInput('id0', 'Data Set A', redRRList, self.processA)
        self.inputs.addInput('id1', 'Data Set B', redRRList, self.processB)

        self.outputs.addOutput('id0', 'intersect Output', redRRVector)
        
        box = widgetBox(self.controlArea,orientation = 'vertical')
        dataSetBox = widgetBox(box,orientation = 'horizontal')
        #pickA = groupBox(dataSetBox, "Dataset A:")
        self.colA = listBox(dataSetBox, label = 'Dataset A:', callback = self.onSelect)
        
        #pickB = groupBox(dataSetBox, "Dataset B:")
        self.colB = listBox(dataSetBox, label = 'Dataset B:', callback = self.onSelect)

        self.resultInfo = textEdit(box,editable=False)
        self.resultInfo.setMaximumWidth(170)
        self.resultInfo.setMaximumHeight(25)
        self.resultInfo.setMinimumWidth(170)
        self.resultInfo.setMinimumHeight(25)
        box.layout().setAlignment(self.resultInfo,Qt.AlignHCenter)
        self.resultInfo.hide()
        self.type = radioButtons(self.bottomAreaLeft,  label = "Perform", 
        buttons = ['Intersect', 'Union', 'Set Difference', 'Set Equal'],setChecked='Intersect',
        orientation='horizontal',callback=self.onTypeSelect)
        
        commitBox = widgetBox(self.bottomAreaRight,orientation = 'horizontal')
        self.bottomAreaRight.layout().setAlignment(commitBox, Qt.AlignBottom)
        self.commitOnInput = redRCheckBox(commitBox, buttons = ['Commit on Selection'],
        toolTips = ['Whenever this selection changes, send data forward.'])
        redRCommitButton(commitBox, "Commit", callback = self.commitFunction)
    
    def onSelect(self):
        if 'Commit on Selection' in self.commitOnInput.getChecked():
            self.commitFunction()
    def onTypeSelect(self):
        self.resultInfo.setPlainText('')
        if self.type.getChecked() =='Set Equal':
            self.resultInfo.show()
        else:
            self.resultInfo.hide()
        
        if 'Commit on Selection' in self.commitOnInput.getChecked():
            self.commitFunction()
            
    def processA(self, data):
        #print 'processA'
        if not data:
            self.colA.update([])
            return 
            
        self.dataA = data.getData()
        colsA = self.R('names('+self.dataA+')',wantType='list')
        self.colA.update(colsA)
        
        if 'Commit on Selection' in self.commitOnInput.getChecked():
            self.commitFunction()
    def processB(self, data):
        if not data:
            self.colB.update([])
            return 
        self.dataB = data.getData()
        colsB = self.R('names('+self.dataB+')',wantType='list') 

        self.colB.update(colsB)

        if 'Commit on Selection' in self.commitOnInput.getChecked():
            self.commitFunction()
    def commitFunction(self):
        if self.dataA and self.dataB:
            h = self.R('intersect(names('+self.dataA+'), names('+self.dataB+'))',wantType='list')
        else: 
            return
            
        if self.colA.selectedItems():
            nameA = self.colA.selectedItems()[0].text()
        else:
            nameA = None
        if self.colB.selectedItems():
            nameB = self.colB.selectedItems()[0].text()
        else:
            nameB = None
            
        if self.type.getChecked() =='Intersect':
            func = 'intersect'
        elif self.type.getChecked() =='Union':
            func = 'union'
        elif self.type.getChecked() =='Set Difference':
            func = 'setdiff'
        elif self.type.getChecked() =='Set Equal':
            func = 'setequal'
        else:
            return 
            
        if nameA and nameB:
            self.R(self.Rvariables['intersect']+'<-%s(y=%s[["%s"]],x=%s[["%s"]])' 
            % (func, self.dataA,nameA,self.dataB,nameB), wantType = 'NoConversion')
        elif len(h) ==1:
            self.R(self.Rvariables['intersect']+'<-%s(y=%s[["%s"]],x=%s[["%s"]])' 
            % (func, self.dataA,h[0],self.dataB,h[0]), wantType = 'NoConversion')
        else:
            return
            
        if self.type.getChecked() =='Set Equal':
            eq = self.R(self.Rvariables['intersect'])
            if eq:
                self.resultInfo.setPlainText('%s is equal to %s' % (nameA, nameB))
            else:
                self.resultInfo.setPlainText('%s is not equal to %s' % (nameA, nameB))
        else:
            newData = redRRVector(data = self.Rvariables["intersect"])
            self.rSend("id0", newData)
            
    def getReportText(self, fileDir):
        return 'Sends the intersecting element, those that are the same, in the two incomming data vectors.\n\n'

