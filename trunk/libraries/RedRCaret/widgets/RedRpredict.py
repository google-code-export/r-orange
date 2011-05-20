"""Predict

Predic outcome from a trained model.

.. helpdoc::
This widget uses a trained data model from a Caret Train widget and a data set to predict new classes.
"""


"""
<widgetXML>
<name>Predict</name>
    <icon>default.png</icon>
    <tags> 
        <tag priority='100'>Caret</tag> 
    </tags>
    <summary>Predict classes or outcome based on a Caret Train model and an optional data collection.</summary>
    <author>
            <authorname>Red-R Core Team</authorname>
            <authorcontact>http://www.red-r.org/contact</authorcontact>
        </author>
</widgetXML>
"""
from OWRpy import * 
import redRGUI, signals

class RedRpredict(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        """.. rrvarnames::"""
        self.setRvariableNames(["predict", 'tempData'])
        self.data = {}
        self.RFunctionParam_object = ''
        self.RFunctionParam_newData = ''
        
        """.. rrsignals::
            :description: `Trained model`
        """
        self.inputs.addInput("object", "object", signals.base.RModelFit, self.processobject)
        
        """.. rrsignals::
            :description: `New data`
        """
        self.inputs.addInput("newData", "newData", [signals.base.RArbitraryList, signals.base.RArbitraryList], self.processnewData)
        
        """.. rrsignals::
            :description: `Prediction output`
        """
        self.outputs.addOutput("predict Output","predict Output", signals.base.RModelFit)
        
        """.. rrgui::"""
        self.testData = redRGUI.base.comboBox(self.controlArea, label = 'Test Data:')
        
        """.. rrgui::"""
        self.classLabels = redRGUI.base.comboBox(self.controlArea, label = 'Class Labels:')
        
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        
        """.. rrgui::"""
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "R Output Window")
    def processobject(self, data):
        
        if data:
            
            self.RFunctionParam_object=data.getData()
            
            self.commitFunction()
        else:
            self.RFunctionParam_object=''
    def processnewData(self, data):
        if data:
            if self.R('class('+data.getData()+')') == 'data.frame':
                self.R(self.Rvariables['tempData']+'<-list(TrainingData = '+data.getData()+')', wantType = 'NoConversion')
                self.RFunctionParam_newData = self.Rvariables['tempData']
            else:
                self.RFunctionParam_newData=data.getData()
            self.testData.update(self.R('names('+self.RFunctionParam_newData+')'))
            self.classLabels.update([''] + self.R('names('+self.RFunctionParam_newData+'[[1]])'))
        else:
            self.RFunctionParam_newData=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_object) == '': return
        if unicode(self.RFunctionParam_newData) == '': 
            self.R(self.Rvariables['predict']+'<-predict.train(object='+unicode(self.RFunctionParam_object)+')')
        else:
            newData = '%s[[\'%s\']]' % (self.RFunctionParam_newData, unicode(self.testData.currentText()))
            if unicode(self.classLabels.currentText()) != '':
                newData = newData+'[, !names('+newData+') %in% c(\''+unicode(self.classLabels.currentText())+'\')]'
            
            self.R(self.Rvariables['predict']+'<-extractPrediction(models=list('+unicode(self.RFunctionParam_object)+'),testX='+newData+')')
        self.R('txt<-c(capture.output(summary('+self.Rvariables['predict']+')), capture.output('+self.Rvariables['predict']+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)
        new = signals.base.RModelFit(self, data = self.Rvariables['predict'])
        self.rSend('predict Output', new)