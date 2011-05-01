"""
<name>Remove Near Zero Var</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>caret:nearZeroVar</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
from libraries.base.qtWidgets.lineEdit import lineEdit as redRlineEdit 
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradioButtons 
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox 
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox 
from libraries.base.qtWidgets.textEdit import textEdit as redRtextEdit 
import libraries.base.signalClasses as signals

class RedRnearZeroVar(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
            OWRpy.__init__(self, **kwargs)
            self.setRvariableNames(["nearZeroVar", "zeroVarRemoved"])
            self.data = {}
            self.require_librarys(["caret"])
            self.RFunctionParam_x = ''
            self.inputs.addInput("x", "x", signals.RDataFrame.RDataFrame, self.processx)
            self.outputs.addOutput("nearZeroVar Output","NZV Analysis", signals.RDataFrame.RDataFrame)
            self.outputs.addOutput('zeroVarRemoved', "Zero Variance Removed", signals.RDataFrame.RDataFrame)
            
            self.RFunctionParamfreqCut_lineEdit = redRlineEdit(self.controlArea, label = "freqCut:", text = '95/5')
            self.RFunctionParamuniqueCut_lineEdit = redRlineEdit(self.controlArea, label = "uniqueCut:", text = '10')
            self.classColumn = redRcomboBox(self.controlArea, label = 'Classes Column', toolTip = 'Sets a column name as a classes column, this column will not be removed even if it is near zero variance, as a concequence, it is also moved to the end of the table.')
            redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
            if data:
                    self.RFunctionParam_x=data.getData()
                    #self.data = data
                    self.classColumn.update(['None'] + self.R('names(%s)' % self.RFunctionParam_x, wantType = 'list'))
                    self.commitFunction()
            else:
                    self.RFunctionParam_x=''
    def commitFunction(self):
            if unicode(self.RFunctionParam_x) == '': return
            injection = []
            if unicode(self.RFunctionParamfreqCut_lineEdit.text()) != '':
                    string = ',freqCut='+unicode(self.RFunctionParamfreqCut_lineEdit.text())+''
                    injection.append(string)
            if unicode(self.RFunctionParamuniqueCut_lineEdit.text()) != '':
                    string = ',uniqueCut='+unicode(self.RFunctionParamuniqueCut_lineEdit.text())+''
                    injection.append(string)
            inj = ''.join(injection)
            if self.classColumn.currentId() == 'None':
                self.R('%(NEW)s<-nearZeroVar(x=%(ORG)s, saveMetrics = TRUE %(INJ)s)' % {'NEW':self.Rvariables['nearZeroVar'], 'ORG':unicode(self.RFunctionParam_x), 'INJ':inj}, wantType = 'NoConversion')
                self.R('%(NEW)s<-%(ORG)s[,!%(NZV)s$nzv]' % {'NEW': self.Rvariables['zeroVarRemoved'], 'ORG':self.RFunctionParam_x, 'NZV':self.Rvariables['nearZeroVar']}, wantType = 'NoConversion')
            else:
                self.R('%(NEW)s<-nearZeroVar(x=%(ORG)s[,-match("%(CLASS)s", colnames(%(ORG)s))], saveMetrics = TRUE %(INJ)s)' % {'NEW':self.Rvariables['nearZeroVar'], 'ORG':unicode(self.RFunctionParam_x), 'INJ':inj, 'CLASS':self.classColumn.currentId()}, wantType = 'NoConversion')
                self.R('%(NEW)s<-cbind(%(ORG)s[,!%(NZV)s$nzv], %(CLASS)s = %(ORG)s[,match("%(CLASS)s", colnames(%(ORG)s))])' % {'NEW': self.Rvariables['zeroVarRemoved'], 'ORG':self.RFunctionParam_x, 'NZV':self.Rvariables['nearZeroVar'], 'CLASS':self.classColumn.currentId()}, wantType = 'NoConversion')
            newData = signals.RDataFrame.RDataFrame(self, data = self.Rvariables["nearZeroVar"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
            #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
            self.rSend("nearZeroVar Output", newData)
            newDF = signals.RDataFrame.RDataFrame(self, data = self.Rvariables['zeroVarRemoved'])
            self.rSend("zeroVarRemoved", newDF)