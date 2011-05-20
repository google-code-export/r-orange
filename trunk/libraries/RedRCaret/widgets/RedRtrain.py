"""Train Model

This widget trains a model to data.

.. helpdoc::

This after processing data this widget is used to fit a predictive model to the data.  Several prediction functions are available to the user.  See the **Method** argument for a list of available models.

All of these can then be used in predictive models with new data.

"""

"""<widgetXML>
<name>Train Model</name>
    <icon>default.png</icon>
    <tags> 
        <tag priority='50'>Caret</tag> 
    </tags>
    <summary>Trains data using one of the Caret training functions.</summary>
        <author>
            <authorname>Red-R Core Team</authorname>
            <authorcontact>http://www.red-r.org/contact</authorcontact>
        </author>
</widgetXML>
"""



from OWRpy import * 
import redRGUI, signals

class RedRtrain(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"])
        
        """.. rrvnames::"""
        self.setRvariableNames(["train", 'tempData'])
        
        self.data = {}
        self.RFunctionParam_data = ''
        self.RFunctionParam_classes = ''
        
        """.. rrsignals::
            :description: `A Caret data model on which to train`
        """
        self.inputs.addInput("data", "Caret Data Model", signals.RedRCaret.CaretData, self.processdata)
        
        """.. rrsignals::
            :description: `A trained Caret model.  This can be used for predictions later.`
        """
        self.outputs.addOutput("train Output","Caret Train Output", signals.base.RModelFit)
        
        
        """.. rrsignals::
            :description: `The final fitted model of the training.`
        """
        self.outputs.addOutput("finalModel", "Final Fitted Model (For Prediction)", caret.CaretModelFit.CaretModelFit)
        
        """.. rrgui::"""
        self.RFunctionParammethod_comboBox = redRGUI.base.comboBox(self.controlArea, label = "Method:", items = [("ada", "ADA Boosted Tree"), ("bagEarth", "Bagged MARS"), ("bagFDA", "Bagged FDA"), ("blackboost", "Black Boosted Tree"), ("cforest", "C Forest Random Forest"), ("ctree", "C Tree Recursive Partitioning"), ("ctree2", "C Tree2 Recursive Partitioning"), ("earth", "Earth MARS"), ("enet", "Elastic Net"), ("fda", "FDA MARS Basis"), ("gamboost", "GAM Boosted Model"), ("gaussprPoly", "Gauss R Poly"), ("gaussprRadial", "Gauss R Radial"), ("gaussprLinear", "Gauss PR Linear"), ("gbm", "GBM Boosted Tree"), ("glm", "GLM"), ("glmboost", "GLM Boosted Tree"), ("glmnet", "GLM Net"), ("gpls", "G PLS"), ("J48", "J48"), ("JRip", "JRip"), ("knn", "K Nearest Neighbors"), ("lars", "LARS"), ("lasso", "Lasso"), ("lda", "LDA"), ("Linda", "Linda"), ("lm", "LM"), ("lmStepAIC", "lmStepAIC"), ("LMT", "LMT"), ("logitBoost", "logitBoost"), ("lssvmPoly", "lssvmPoly"), ("lssvmRadial", "lssvmRadial"), ("lvq", "LVQ"), ("M5Rules", "M5Rules"), ("mda", "MDA"), ("multinom", "Multinorm"), ("nb", "NB"), ("nnet", "Neural Net"), ("nodeHarvest", "Node Harvest"), ("OneR", "OneR"), ("pam", "PAM"), ("pcaNNet", "PCA NN"), ("pcr", "PCR"), ("pda", "PDA"), ("pda2", "PDA2"), ("penalized", "Penalized"), ("pls", "PLS"), ("ppr", "PPR"), ("qda", "QDA"), ("QdaCov", "QDA Cov"), ("rda", "RDA"), ("rf", "Random Forest"), ("rlm", "RLM"), ("rpart", "R Part"), ("rvmLinear", "RVM Linear"), ("rvmPoly", "RVM Poly"), ("rvmRadial", "RVM Radial"), ("sda", "SDA"), ("sddaLDA", "SDDA LDA"), ("sddaQDA", "SDDA QDA"), ("slda", "SLDA"), ("smda", "SMDA"), ("sparseLDA", "Spars LDA"), ("spls", "SPLS"), ("stepLDA", "Step LDA"), ("stepQDA", "Step QDA"), ("superpc", "Super PC"), ("svmPoly", "SVM Poly"), ("svmRadial", "SVM Radial"), ("svmLinear", "SVM Linear"), ("treebag", "Tree Bag"), ("vbmpRadial", "VBMP Radial")])
        
        """.. rrgui::"""
        self.RFunctionParam_tuneLengthSpin = redRGUI.base.spinBox(self.controlArea, label = 'Tune Length:', min = 1, value = 5)
        """.. rrgui::"""
        self.otherParameters = redRGUI.base.lineEdit(self.controlArea, label = 'Other Parameters (Advanced):')
        
        """.. rrgui::"""
        self.tuneParameters = redRGUI.base.lineEdit(self.controlArea, label = 'Tune Parameters (Advanced):')
        outputTabs = redRGUI.base.tabWidget(self.controlArea)
        textBox = outputTabs.createTabPage('Training Summary')
        """.. rrgui::"""
        self.RoutputWindow = redRGUI.base.textEdit(textBox, label = "R Output Window", displayLabel = False)
        
        imageBox = outputTabs.createTabPage('Training Plot')
        
        """.. rrgui::"""
        self.RFunctionParam_plotType = redRGUI.base.comboBox(imageBox, label = 'Plot Type', items = [('scatter', 'Scatter'), ('level', 'Level'), ('line', 'Line')], callback = self.replot)
        
        """.. rrgui::"""
        self.plotArea = redRGUI.base.graphicsView(imageBox, label = 'Training Plot', displayLabel = False)
        
        
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        
        if data:
            self.RFunctionParam_data=data.getData()
            self.RFunctionParam_classes = data.getClasses()
            
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': 
            self.status.setText('No data to work with')
            return
        if unicode(self.RFunctionParam_classes) == '':
            self.status.setText('No classes to work with')
            return
        injection = []
        # if unicode(self.RFunctionParamcustomArgs_lineEdit.text()) != '':
            # string =','+unicode(self.RFunctionParamcustomArgs_lineEdit.text())
            # injection.append(string)
        #if unicode(self.RFunctionParamtrControl_lineEdit.text()) != '':
        string = ',trControl= trainControl(verbose = FALSE, returnResamp = "all")'#+unicode(self.RFunctionParamtrControl_lineEdit.text())+''
        injection.append(string)
        string = ',method=\"'+unicode(self.RFunctionParammethod_comboBox.currentId())+'\"'
        injection.append(string)
        if unicode(self.otherParameters.text()) != '':
            injection.append(',%s' % unicode(self.otherParameters.text()))
        if unicode(self.tuneParameters.text()) != '':
            injection.append(',tuneGrid = expand.grid(%s)' % unicode(self.tuneParameters.text()))
        injection.append(', tuneLength = %s' % str(self.RFunctionParam_tuneLengthSpin.value()))
        inj = ''.join(injection)
        self.R(self.Rvariables['train']+'<-train(x='+self.RFunctionParam_data+', y = '+self.RFunctionParam_classes+inj+')')
        newData = signals.base.RModelFit(self, data = self.Rvariables["train"])
        self.rSend("train Output", newData)
        newDataModel = caret.CaretModelFit.CaretModelFit(self, data = self.Rvariables['train']+'$finalModel')
        self.rSend("finalModel", newDataModel)
        self.RoutputWindow.clear()
        tmp = self.R('paste(capture.output('+self.Rvariables['train']+'), collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)
        
        self.replot()
        
    def replot(self):
        if 'parameter' in self.R('names(%s$resample)' % self.Rvariables['train'], wantType = 'list') and self.R('%s$resample$parameter[1]' % self.Rvariables['train'], wantType = 'list') != 'none':
            pass
        else:
            self.plotArea.plot(query = '%s, plotType = \'%s\'' % (self.Rvariables['train'], self.RFunctionParam_plotType.currentId())) 
            