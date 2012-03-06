"""Caret Predictions and Probabilities

Calculate predictions and their probabilities of being correct.

.. helpdoc::

Generates two data tables one for predictions and one for probabilities of the supplied samples being of a class.
"""

"""<widgetXML>
<name>Caret Predictions and Probabilities</name>
    <icon>default.png</icon>
    <tags>
        <tag priority = '400'>Caret</tag>
    </tags>
    <summary>Generates two data tables one for predictions and one for probabilities of the supplied samples being of a class.</summary>
    <author>
            <authorname>Red-R Core Development Team</authorname>
            <authorcontact>www.red-r.org</authorcontact>
        </author>
    </widgetXML>
"""
from OWRpy import * 
import redRGUI, signals
import libraries.RedRCaret.signalClasses as caret

class extractPredsProbs(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        self.setRvariableNames(["preds", 'probs'])
        self.data = {}
        self.RFunctionParam_predictions = ''
        self.RFunctionParam_classes = ''
        
        """.. rrsignals::
            :description: `Prediction model.`
        """
        self.inputs.addInput("data", "Fitted Prediction Model", signals.base.RModelFit, self.processdata, multiple = True)
        
        """.. rrsignals::
            :description: `Classification Data`
        """
        self.inputs.addInput('predicationData', 'Classification Data', caret.CaretData.CaretData, self.processpreds)
        
        """.. rrsignals::
            :description: `Data table of predictions, this can be output as a table.`
        """
        self.outputs.addOutput("predictions","Caret Predictions", signals.base.RDataFrame)
        
        """.. rrsignals::
            :description: `Data table of probabilities, this can be output as a table.`
        """
        self.outputs.addOutput("probabilities", "Caret Probabilities", signals.base.RDataFrame)
        
        self.widgetLabel = redRGUI.base.widgetLabel(self.bottomAreaLeft, label = '')
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "R Output Window")
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processpreds(self, data):
        if data:
            self.RFunctionParam_predictions = data.getData()
            self.RFunctionParam_classes = data.getClasses()
            self.commitFunction()
        else:
            self.RFunctionParam_predictions = ''
            self.RFunctionParam_classes = ''
    def processdata(self, data, id):
        
        if data:
            self.data[id] = data.getData()
            self.commitFunction()
        else:
            self.data[id] = None
            
    def commitFunction(self):
        if self.RFunctionParam_predictions == '':
            self.status.setText('No classification data')
            return
        models = [i for i in self.data.values() if i != None]
        if len(models) == 0:
            self.status.setText('No data to predict on')
            return
        dataInputs = {'MODEL':','.join(models), 'PRED':self.Rvariables['preds'], 'PROB':self.Rvariables['probs']}
        if self.RFunctionParam_predictions != '':
            dataInputs['testX'] = self.RFunctionParam_predictions
        else:
            dataInputs['testX'] = 'NULL'
        if self.RFunctionParam_classes != '':
            dataInputs['testY'] = self.RFunctionParam_classes
        else:
            dataInputs['testY'] = 'NULL'
            
        tmp = ''
        try:
            self.R('%(PRED)s<-extractPrediction(list(%(MODEL)s), testX = %(testX)s, testY = %(testY)s)' % dataInputs, wantType = 'NoConversion') 
            newDataPred = signals.base.RDataFrame(self, data = self.Rvariables['preds'])
            self.rSend("predictions", newDataPred)
            tmp += 'Predictions\n\n'
            tmp += self.R('paste(capture.output(str('+self.Rvariables['preds']+')), collapse ="\n")') + '\n\n'
        except RuntimeError:
            self.widgetLabel.setText('Could not format predicitons')
            self.rSend('predictions', None)
            
        try:
            self.R('%(PROB)s<-extractProb(list(%(MODEL)s), testX = %(testX)s, testY = %(testY)s)' % dataInputs, wantType = 'NoConversion')
            newDataProbs = signals.base.RDataFrame(self, data = self.Rvariables['probs'])
            self.rSend('probabilities', newDataProbs)
            tmp += 'Probabilities\n\n'
            tmp += self.R('paste(capture.output(str('+self.Rvariables['probs']+')), collapse ="\n")')
        except RuntimeError:
            self.widgetLabel.setText('Could not format predictions')
            self.rSend('probabilities', None)
        
        
        
        self.RoutputWindow.clear()
        self.RoutputWindow.insertPlainText(tmp)