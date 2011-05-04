"""
<name>Caret Data Model</name>
<description>A Data container making widget to handle Caret Data Models.  In general, all this does is to accept a data-frame and optional vector of class predictors and class labels respectively.  If only a data-frame is attached, then the user can select a column from the table to represent the predictors.</description>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
from libraries.base.qtWidgets.widgetLabel import widgetLabel as redRwidgetLabel
import libraries.base.signalClasses as signals
import libraries.RedRCaret.signalClasses as caret

class caretDataModel(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret", 'ada', 'affy', 'caTools', 'class', 'e1071', 'earth', 'elasticnet', 'ellipse', 'fastICA', 'foba', 'foreach', 'gam', 'GAMens', 'gbm', 'glmnet', 'gpls', 'grid', 'hda', 'HDclassif', 'ipred', 'kernlab', 'klaR', 'lars', 'LogicForest', 'logicFS', 'LogicReg', 'MASS', 'mboost', 'mda', 'mgcv', 'mlbench', 'neuralnet', 'nnet', 'nodeHarvest', 'pamr', 'partDSA', 'party', 'penalized', 'pls', 'proxy', 'quantregForest', 'randomForest', 'RANN', 'rda', 'relaxo', 'rocc', 'rpart', 'rrcov', 'RWeka', 'sda', 'SDDA', 'sparseLDA', 'spls', 'stepPlr', 'superpc', 'vbm'])
        self.setRvariableNames(["dataModel"])
        
        self.RFunctionParam_data = ''
        self.RFunctionParam_predictors = ''
        self.inputs.addInput("x", "Data Table", signals.RDataFrame.RDataFrame, self.processx)
        self.inputs.addInput("data", "Class Vector", signals.RVector.RVector, self.processdata)
        self.outputs.addOutput('caretModel',"Reduced Data Table", caret.CaretData.CaretData)
        
        self.classLabels = redRcomboBox(self.controlArea, label = 'Class Column')
        self.myLable = redRwidgetLabel(self.controlArea, label = '')
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        
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
            if self.R('length(%s[,1])' % self.RFunctionParam_data) != self.R('length(%s)' % self.RFunctionParam_predictors):
                self.status.setText('Data not of the same length, these are not valid pairs')
                return
            classes = self.RFunctionParam_predictors
            data = self.RFunctionParam_data
            
        newData = caret.CaretData.CaretData(self, data = data, classes = classes)
        
        self.rSend("caretModel", newData)