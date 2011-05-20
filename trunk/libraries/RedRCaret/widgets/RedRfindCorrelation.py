"""PreProcess Data

Process data for training.

.. helpdoc::

This widget pre-processes data so that it can be more efficiently used in prediction.  This involves removing predictors with near zero variance (using nearZeroVar()), predictors with high correlation (using findCorrelation()), and reducing predictors in design matrices.
"""


"""<widgetXML>
<name>PreProcess Data</name>
    <icon>default.png</icon>
    <tags> 
        <tag priority='47'>Caret</tag> 
    </tags>
    <summary>Find internal correlations within data and provide an index of items to remove that will resolve these correlations.</summary>
        <author>
            <authorname>Red-R Core Team</authorname>
            <authorcontact>http://www.red-r.org/contact</authorcontact>
        </author>
</widgetXML>
"""
from OWRpy import * 
import redRGUI, signals
import libraries.RedRCaret.signalClasses as caret

class RedRfindCorrelation(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        
        """ ..rrvarnames::"""
        self.setRvariableNames(["findCorrelation", "nearZero", "findCorrelationOutput", "preProcess"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.RFunctionParam_data = ''
        #self.inputs.addInput("x", "Correlation Matrix", signals.base.RMatrix, self.processx)
        
        """.. rrsignals::
            :description: `A Caret data signal or data container`
        """
        self.inputs.addInput("data", "Data Table / Sample List", caret.CaretData.CaretData , self.processdata)
        
        """.. rrsignals::
            :description: `A processed Caret data signal`
        """
        self.outputs.addOutput("findCorrelation Output","Reduced Data Table", caret.CaretData.CaretData)
        
        """.. rrsignals::
            :description: `A special Caret model for use in applying preprocessing to other data sets.  This is a consequence of Caret's configuration and, confusing as it is, one can use Predict to apply these predictions to a new data container.`
        """
        self.outputs.addOutput("preprocess model", "PreProcess Model (To Calibrate Test Data)", caret.CaretModelFit.CaretModelFit)
        grid = redRGUI.base.gridBox(self.controlArea)
        
        """.. rrgui::"""
        self.nearZero = redRGUI.base.radioButtons(grid.cell(0,0), label = 'Remove Near Zero Variance Predictors?', buttons = ['Yes', 'No'], setChecked = 'Yes', callback = self.nzvShowHide)
        
        self.nzvBox = redRGUI.base.widgetBox(grid.cell(0,0))
        
        """.. rrgui::"""
        self.freqCut = redRGUI.base.lineEdit(self.nzvBox, label = 'Frequency Cut:', text = '95/5')
        
        """.. rrgui::"""
        self.uniqueCut = redRGUI.base.lineEdit(self.nzvBox, label = 'Unique Cut:', text = '10')
        
        """.. rrgui::"""
        self.preProcess = redRGUI.base.radioButtons(grid.cell(0,1), label = 'Perform Pre Processing?', buttons = ['Yes', 'No'], setChecked = 'Yes', callback = self.nzvShowHide)
        
        
        """.. rrgui::"""
        self.preprocessMethodsCombo = redRGUI.base.listBox(grid.cell(0,1), label = 'Pre Process Methods', items = [("BoxCox", "BoxCox"), ("center", "Center"), ("scale", "Scale"), ("range", "Range"), ("knnImpute", "KNN Impute"), ("bagImpute", "Bag Impute"), ("pca", "Principal Components"), ("ica", "Independent Components"), ("spatialSign", "Spatial Sign")])
        
        """.. rrgui::"""
        self.preprocessMethodsCombo.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        """.. rrgui::"""
        self.preprocessMethodsCombo.setSelectedIds(["center", "scale"])
        
        """.. rrgui::"""
        self.preprocessTresh = redRGUI.base.spinBox(grid.cell(0,2), label = 'Pre Process Threshold:', min = 0, value = 0.95, decimals = 3)
        
        """.. rrgui::"""
        self.preProcessNARM = redRGUI.base.radioButtons(grid.cell(0,2), label = 'Remove NA?', buttons = [('TRUE', 'Yes'), ('FALSE', 'No')], setChecked = 'TRUE', callback = self.nzvShowHide)
        
        """.. rrgui::"""
        self.preProcessKNN = redRGUI.base.spinBox(grid.cell(0,2), label = 'Pre Process Threshold:', min = 0, value = 5, decimals = 0)
        
        """.. rrgui::"""
        self.preProcessKNNSUM = redRGUI.base.comboBox(grid.cell(0,2), label = 'KNN Summary', items = [('mean', 'Mean'), ('median', 'Median'), ('min', 'Minimum'), ('max', 'Maximum')])
        
        """.. rrgui::"""
        self.preProcessFUDGE = redRGUI.base.spinBox(grid.cell(0,2), label = 'Fudge Value:', min = 0, value = 0.2, decimals = 3)
        
        """.. rrgui::"""
        self.preProcessNUMUNI = redRGUI.base.spinBox(grid.cell(0,2), label = 'Box-Cot Unique Values', min = 2, value = 3, decimals = 0)
        
        """.. rrgui::"""
        self.RFunctionParamcutoff_spinBox = redRGUI.base.spinBox(grid.cell(0,2), label = "Max Correlation Coef (/100):", min = 1, max = 99, value = 90)
        
        """.. rrgui::"""
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        
        """.. rrgui::"""
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "R Output Window")
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
        
    