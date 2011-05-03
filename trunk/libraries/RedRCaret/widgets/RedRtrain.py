"""
<name>train</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>caret:train</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
from libraries.base.qtWidgets.RFormulaEntry import RFormulaEntry as redRRFormulaEntry
import libraries.base.signalClasses as signals
import libraries.RedRCaret.signalClasses as caret

class RedRtrain(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["caret"]) #, "ada", "affy", "caTools", "class", "e1071", "earth", "elasticnet", "ellipse", "fastICA", "foba", "foreach", "gam", "GAMens", "gbm", "glmnet", "gpls", "grid", "hda", "HDclassif", "ipred", "kernlab", "klaR", "lars", "LogicForest", "logicFS", "LogicReg", "MASS", "mboost", "mda", "mgcv", "mlbench", "neuralnet", "nnet", "nodeHarvest", "pamr", "partDSA", "party", "penalized", "pls", "proxy", "quantregForest","randomForest", "RANN", "rda", "relaxo", "rocc", "rpart", "rrcov", "RWeka", "sda", "SDDA", "sparseLDA", "spls", "stepPlr", "superpc", "vbm"])
        self.setRvariableNames(["train", 'tempData'])
        self.data = {}
        self.RFunctionParam_data = ''
        self.RFunctionParam_classes = ''
        self.inputs.addInput("data", "Caret Data Model", caret.CaretData.CaretData, self.processdata)
        self.outputs.addOutput("train Output","Caret Train Output", signals.RModelFit.RModelFit)
        self.outputs.addOutput("finalModel", "Final Fitted Model (For Prediction)", caret.CaretModelFit.CaretModelFit)
        
        self.RFunctionParammethod_comboBox = redRcomboBox(self.controlArea, label = "Method:", items = [("ada", "ADA Boosted Tree"), ("bagEarth", "Bagged MARS"), ("bagFDA", "Bagged FDA"), ("blackboost", "Black Boosted Tree"), ("cforest", "C Forest Random Forest"), ("ctree", "C Tree Recursive Partitioning"), ("ctree2", "C Tree2 Recursive Partitioning"), ("earth", "Earth MARS"), ("enet", "Elastic Net"), ("fda", "FDA MARS Basis"), ("gamboost", "GAM Boosted Model"), ("gaussprPoly", "Gauss R Poly"), ("gaussprRadial", "Gauss R Radial"), ("gaussprLinear", "Gauss PR Linear"), ("gbm", "GBM Boosted Tree"), ("glm", "GLM"), ("glmboost", "GLM Boosted Tree"), ("glmnet", "GLM Net"), ("gpls", "G PLS"), ("J48", "J48"), ("JRip", "JRip"), ("knn", "K Nearest Neighbors"), ("lars", "LARS"), ("lasso", "Lasso"), ("lda", "LDA"), ("Linda", "Linda"), ("lm", "LM"), ("lmStepAIC", "lmStepAIC"), ("LMT", "LMT"), ("logitBoost", "logitBoost"), ("lssvmPoly", "lssvmPoly"), ("lssvmRadial", "lssvmRadial"), ("lvq", "LVQ"), ("M5Rules", "M5Rules"), ("mda", "MDA"), ("multinom", "Multinorm"), ("nb", "NB"), ("nnet", "Neural Net"), ("nodeHarvest", "Node Harvest"), ("OneR", "OneR"), ("pam", "PAM"), ("pcaNNet", "PCA NN"), ("pcr", "PCR"), ("pda", "PDA"), ("pda2", "PDA2"), ("penalized", "Penalized"), ("pls", "PLS"), ("ppr", "PPR"), ("qda", "QDA"), ("QdaCov", "QDA Cov"), ("rda", "RDA"), ("rf", "RF"), ("rlm", "RLM"), ("rpart", "R Part"), ("rvmLinear", "RVM Linear"), ("rvmPoly", "RVM Poly"), ("rvmRadial", "RVM Radial"), ("sda", "SDA"), ("sddaLDA", "SDDA LDA"), ("sddaQDA", "SDDA QDA"), ("slda", "SLDA"), ("smda", "SMDA"), ("sparseLDA", "Spars LDA"), ("spls", "SPLS"), ("stepLDA", "Step LDA"), ("stepQDA", "Step QDA"), ("superpc", "Super PC"), ("svmPoly", "SVM Poly"), ("svmRadial", "SVM Radial"), ("svmLinear", "SVM Linear"), ("treebag", "Tree Bag"), ("vbmpRadial", "VBMP Radial")])
        
        self.otherParameters = redRlineEdit(self.controlArea, label = 'Other Parameters (Advanced):')
        self.tuneParameters = redRlineEdit(self.controlArea, label = 'Tune Parameters (Advanced):')
        
        self.RoutputWindow = redRtextEdit(self.controlArea, label = "R Output Window")
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
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
        inj = ''.join(injection)
        self.R(self.Rvariables['train']+'<-train(x='+self.RFunctionParam_data+', y = '+self.RFunctionParam_classes+inj+')')
        newData = signals.RModelFit.RModelFit(self, data = self.Rvariables["train"])
        self.rSend("train Output", newData)
        newDataModel = caret.CaretModelFit.CaretModelFit(self, data = self.Rvariables['train']+'$finalModel')
        self.rSend("finalModel", newDataModel)
        self.RoutputWindow.clear()
        tmp = self.R('paste(capture.output('+self.Rvariables['train']+'), collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)