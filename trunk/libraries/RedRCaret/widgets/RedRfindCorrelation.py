"""
<name>Process Predictors</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>caret:findCorrelation</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
from libraries.base.qtWidgets.gridBox import gridBox as redRGridBox
import libraries.base.signalClasses as signals
import libraries.RedRCaret.signalClasses as caret

class RedRfindCorrelation(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        self.setRvariableNames(["findCorrelation", "nearZero", "findCorrelationOutput", "preProcess"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.RFunctionParam_data = ''
        #self.inputs.addInput("x", "Correlation Matrix", signals.RMatrix.RMatrix, self.processx)
        self.inputs.addInput("data", "Data Table / Sample List", caret.CaretData.CaretData , self.processdata)
        self.outputs.addOutput("findCorrelation Output","Reduced Data Table", caret.CaretData.CaretData)
        self.outputs.addOutput("preprocess model", "PreProcess Model (To Calibrate Test Data)", caret.CaretModelFit.CaretModelFit)
        grid = redRGridBox(self.controlArea)
        self.nearZero = redRRadioButtons(grid.cell(0,0), label = 'Remove Near Zero Variance Predictors?', buttons = ['Yes', 'No'], setChecked = 'Yes', callback = self.nzvShowHide)
        
        self.nzvBox = redRWidgetBox(grid.cell(0,0))
        self.freqCut = redRLineEdit(self.nzvBox, label = 'Frequency Cut:', text = '95/5')
        self.uniqueCut = redRLineEdit(self.nzvBox, label = 'Unique Cut:', text = '10')
        
        self.preProcess = redRRadioButtons(grid.cell(0,1), label = 'Perform Pre Processing?', buttons = ['Yes', 'No'], setChecked = 'Yes', callback = self.nzvShowHide)
        self.preprocessMethodsCombo = redRListBox(grid.cell(0,1), label = 'Pre Process Methods', items = [("BoxCox", "BoxCox"), ("center", "Center"), ("scale", "Scale"), ("range", "Range"), ("knnImpute", "KNN Impute"), ("bagImpute", "Bag Impute"), ("pca", "Principal Components"), ("ica", "Independent Components"), ("spatialSign", "Spatial Sign")])
        self.preprocessMethodsCombo.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.preprocessMethodsCombo.setSelectedIds(["center", "scale"])
        
        self.preprocessTresh = redRSpinBox(grid.cell(0,2), label = 'Pre Process Threshold:', min = 0, value = 0.95, decimals = 3)
        self.preProcessNARM = redRRadioButtons(grid.cell(0,2), label = 'Remove NA?', buttons = [('TRUE', 'Yes'), ('FALSE', 'No')], setChecked = 'TRUE', callback = self.nzvShowHide)
        self.preProcessKNN = redRSpinBox(grid.cell(0,2), label = 'Pre Process Threshold:', min = 0, value = 5, decimals = 0)
        self.preProcessKNNSUM = redRComboBox(grid.cell(0,2), label = 'KNN Summary', items = [('mean', 'Mean'), ('median', 'Median'), ('min', 'Minimum'), ('max', 'Maximum')])
        self.preProcessFUDGE = redRSpinBox(grid.cell(0,2), label = 'Fudge Value:', min = 0, value = 0.2, decimals = 3)
        self.preProcessNUMUNI = redRSpinBox(grid.cell(0,2), label = 'Box-Cot Unique Values', min = 2, value = 3, decimals = 0)
        
        self.RFunctionParamcutoff_spinBox = redRSpinBox(grid.cell(0,2), label = "Max Correlation Coef (/100):", min = 1, max = 99, value = 90)
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRtextEdit(self.controlArea, label = "R Output Window")
    def nzvShowHide(self):
        if unicode(self.nearZero.getChecked()) == 'Yes':
            self.nzvBox.show()
        else:
            self.nzvBox.hide()
    
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            self.RFunctionParam_classes = data.getClasses()
        else:
            self.RFunctionParam_data=''
            self.RFunctionParam_classes = ''
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': 
            self.status.setText('No Data To Work On')
            return
        ## findCorrelation params
        injection = []
        string = ',cutoff='+unicode(float(self.RFunctionParamcutoff_spinBox.value())/100)+''
        injection.append(string)
        inj = ''.join(injection)
        
        ## nzv parame
        nzvInjection = []
        nzvInjection.append(',freqCut = '+unicode(self.freqCut.text()))
        nzvInjection.append(',uniqueCut = '+unicode(self.uniqueCut.text()))
        nzvInj = ''.join(nzvInjection)
        
        ## if nzv checked
        if unicode(self.nearZero.getChecked()) == 'Yes':
            self.R('%s<-nearZeroVar(%s, %s)' % (unicode(self.Rvariables['nearZero']), unicode(self.RFunctionParam_data),  unicode(nzvInj)))
            cor = 'cor(%s)' % unicode(self.RFunctionParam_data)
            self.R(self.Rvariables['findCorrelation']+'<-findCorrelation(x=%s %s)' % (cor, inj))
            remove = 'c(%s, %s)' % (self.Rvariables['findCorrelation'], self.Rvariables['nearZero'])
        ## else nzv not checked
        else:
            cor = 'cor(%s)' % unicode(self.RFunctionParam_data)
            self.R(self.Rvariables['findCorrelation']+'<-findCorrelation(x=%s %s)' % (cor, inj))
            remove = self.Rvariables['findCorrelation']
            
        ## at this point we should remove those columns that do not supply any data or that are correlated.
        self.R(self.Rvariables['findCorrelationOutput']+'<-'+self.RFunctionParam_data+'[, -'+remove+']', wantType = 'NoConversion')
        
        ## preprocess fits a model that must then be used as a predictor for each set of data.  In this case there is a predition function that should be run, in other cases the prediction function should be run on other attached data sources.
        if self.preProcess.getChecked() == 'Yes':
            self.R('%(OUTPUT)s<-preProcess(%(DATA)s, method = %(METHOD)s, threshold = %(THRESH)s, na.remove = %(NARM)s, k = %(KNN)s, knnSummary = %(KNNSUM)s, outcome = %(OUTCOME)s, fudge = %(FUDGE)s, numUnique = %(NUMUNI)s)' %
                {
                    'OUTPUT':self.Rvariables['preProcess']
                    ,'DATA':'%s' % self.Rvariables['findCorrelationOutput']
                    ,'METHOD':'c(%s)' % (','.join(['"%s"' % i for i in self.preprocessMethodsCombo.selectedIds()]))
                    ,'THRESH':str(self.preprocessTresh.value())
                    ,'NARM':self.preProcessNARM.getCheckedId()
                    ,'KNN':str(self.preProcessKNN.value())
                    ,'KNNSUM':self.preProcessKNNSUM.currentId()
                    ,'OUTCOME':'%s' % self.RFunctionParam_classes
                    ,'FUDGE':str(self.preProcessFUDGE.value())
                    ,'NUMUNI':str(self.preProcessNUMUNI.value())
                }
                , wantType = 'NoConversion')
            self.R('%(OUTPUT)s<-predict(%(PREPRO)s, %(OUTPUT)s)' % {
                'OUTPUT':self.Rvariables['findCorrelationOutput'],
                'PREPRO':self.Rvariables['preProcess']
                },
                wantType = 'NoConversion')
        newData = caret.CaretData.CaretData(self, data = self.Rvariables['findCorrelationOutput'], classes = self.RFunctionParam_classes, parent = self.Rvariables['findCorrelationOutput'])
        self.rSend("findCorrelation Output", newData)
        newDataPreprocess = caret.CaretModelFit.CaretModelFit(self, data = self.Rvariables['preProcess'])
        self.rSend("preprocess model", newDataPreprocess)
        self.RoutputWindow.clear()
        self.RoutputWindow.insertPlainText('Removed %s samples from the data.' % self.R('length('+self.Rvariables['findCorrelation']+')'))
        
    