"""Caret Data Model

Make a data model for the Caret package.

.. helpdoc::

This widget is the first widget to use in the Caret package.  This formats data in a form that is more condusive for the Caret package by separating predictors from class labels and keeping them in the same signal.
"""

"""<widgetXML>
<name>Caret Data Model</name>
    <icon>default.png</icon>
    <tags>
        <tag priority='10'>Caret</tag>
    </tags>
    <summary>Make a data model that can be used in other Caret widgets.</summary>
    <author>
            <authorname>Red-R Core Development Team</authorname>
            <authorcontact>www.red-r.org</authorcontact>
        </author>
    </widgetXML>
"""
from OWRpy import * 
import redRGUI, signals
import libraries.RedRCaret.signalClasses as caret

class caretDataModel(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        self.setRvariableNames(["dataModel"])
        
        self.RFunctionParam_data = ''
        self.RFunctionParam_predictors = ''
        
        """.. rrsignals::
            :description: `Input data table, this can have optionally, class predictors.`
        """
        self.inputs.addInput("x", "Data Table", signals.base.RDataFrame, self.processx)
        
        """..rrsignals::
            :description: `An optional vector of classes.`
        """
        self.inputs.addInput("data", "Class Vector", signals.base.RVector, self.processdata)
        
        """.. rrsignals::
            :description: `The complete Caret Data Container.`
        """
        self.outputs.addOutput('caretModel',"Reduced Data Table", caret.CaretData.CaretData)
        
        """.. rrgui::"""
        self.classLabels = redRGUI.base.comboBox(self.controlArea, label = 'Class Column')
        
        self.myLable = redRGUI.base.widgetLabel(self.controlArea, label = '')
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        
    def processx(self, data):
        if data:
            self.RFunctionParam_data = data.getData()
            self.myLable.setText('Select column representing classes')
            self.classLabels.update(self.R('names(%s)' % self.RFunctionParam_data, wantType = 'list'))
        else:
            self.RFunctionParam_data = ''
            
    def processdata(self, data):
        if data:
            self.RFunctionParam_predictors = data.getData()
            self.myLable.setText('Prediction Vector attached, Class Column will be ignored')
        else:
            self.RFunctionParam_predictors = ''
            
    def commitFunction(self):
        if self.RFunctionParam_data == '':
            self.status.setText('No Data to work with')
            
        if self.RFunctionParam_predictors == '':
            classes = '%s$%s' % (self.RFunctionParam_data, self.classLabels.currentId())
            self.R('%(NEW)s<-%(ORG)s; %(NEW)s$%(COL)s<-NULL' % {'NEW':self.Rvariables['dataModel'], 'ORG':self.RFunctionParam_data, 'COL':self.classLabels.currentId()}, wantType = 'NoConversion')
            data = self.Rvariables['dataModel']
        else:
            if self.R('length(%s[,1])' % self.RFunctionParam_data)%self.R('length(%s)' % self.RFunctionParam_predictors) != 0:
                self.status.setText('Data not of the same length, these are not valid pairs')
                return
            classes = self.RFunctionParam_predictors
            data = self.RFunctionParam_data
            
        newData = caret.CaretData.CaretData(self, data = data, classes = classes)
        
        self.rSend("caretModel", newData)