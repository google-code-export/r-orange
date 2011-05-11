"""
<name>Plate Normailze</name>
"""
from OWRpy import *

from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton
import libraries.base.signalClasses as signals 
import redR

class plateNormalize(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_data = ''
        self.setRvariableNames(["norm"])
        self.require_librarys(["reshape", "gregmisc"])
        self.inputs.addInput("data", "Data Table", signals.RDataFrame.RDataFrame, self.processdata)
        self.outputs.addOutput("data", "Data Table", signals.RDataFrame.RDataFrame) 
        """Input sigals are base.RDataFrame, Output signals are base.RDataFrame"""
        
        self.GUIPARAM_Grouping = comboBox(self.controlArea, label = "Sample Groupings")
        self.GUIPARAM_NormGroup = comboBox(self.controlArea, label = "Normalization Groupings", callback = self.setGUIPARAM_NormPoint)
        self.GUIPARAM_NormPoint = comboBox(self.controlArea, label = "Normalization Point")
        self.GUIPARAM_Measure = comboBox(self.controlArea, label = "Measure Values")
        """
        .. rrgui:: Sample Groupings; the column that will be used to normalize against.

        .. rrgui:: Normalization Groupings; the column that holds the normalization descriptors for each group.
        
        .. rrgui:: Normalization Point; the point in the Normalization Groupings that the Sample Groupings values will be normalized to.
        
        .. rrgui:: Measure Values; the values that will be normalized.
        """
        
        
        self.GUIOUTPUT_Text = textEdit(self.controlArea, label = "Data Sample")
        
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def setGUIPARAM_NormPoint(self):
        """Set the data for the GUIPARAM_NormPoint"""
        if self.RFunctionParam_data == '': return
        normPoints = []
        rDataPoints = self.R('as.character(%s$%s)' % (self.RFunctionParam_data, self.GUIPARAM_NormGroup.currentId()), wantType = redR.CONVERT)
        for p in rDataPoints:
            if p not in normPoints: normPoints.append(p)
        self.GUIPARAM_NormPoint.update(normPoints)
    def processdata(self, data):
        """Process new data and set the data for the GUI"""
        if data:
            self.RFunctionParam_data=data.getData()
            names = self.R('names(%s)' % self.RFunctionParam_data, wantType = redR.CONVERT)
            self.GUIPARAM_Grouping.update(names)
            self.GUIPARAM_NormGroup.update(names)
            self.GUIPARAM_Measure.update(names)
            self.setGUIPARAM_NormPoint()
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
            
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': 
            self.status.setText('No data to work with')
            return
        if self.GUIPARAM_Grouping.currentId() == self.GUIPARAM_Measure.currentId():
            self.status.setText('Values can\'t be the same')
            return
        """Now we can do fun stuff!! Out goal is to extract all of the values for the GUIPARAM_Measure where the GUIPARAM_Grouping and the GUIPARAM_NormGroup are the same and the GUIPARAM_NormGroup is equal to the GUIPARAM_NormPoint.  Then the means of these are calculated and used to divide all measurements in the groupings by.  Then the data is placed back into a table that is identical in shape to the first data table except in that the norm point will be centered about 1 for each of the groupings and all other measures adjusted for the norm point."""
        
        """Step 1, we recast the data to aggregate over the GUIPARAM_Grouping and GUIPARAM_NormGroup with measure values as GUIPARAM_Measure"""
        opts = {'DATA':self.RFunctionParam_data, 'GROUP':self.GUIPARAM_Grouping.currentId(), 'NORMGROUP':self.GUIPARAM_NormGroup.currentId(), 'MES':self.GUIPARAM_Measure.currentId(), 'NEWDATA':self.Rvariables['norm'], 'NORMPOINT':self.GUIPARAM_NormPoint.currentId()}
        self.R('rdata<-recast(%(DATA)s, %(GROUP)s ~ %(NORMGROUP)s, id.var = c("%(GROUP)s", "%(NORMGROUP)s"), measure.var = c("%(MES)s"), fun.aggregate = mean)' % opts, wantType = redR.NOCONVERSION)
        self.R('%(NEWDATA)s<-data.frame()' % opts, wantType = redR.NOCONVERSION)
        self.R(
"""for (l in levels(as.factor(rdata$%(GROUP)s))){
    sData<-subset(%(DATA)s, as.character(%(DATA)s$%(GROUP)s) == l)
    sData$Norm<-as.numeric(sData$%(MES)s)/as.numeric(subset(rdata, as.character(rdata$%(GROUP)s) == l)[,"%(NORMPOINT)s"])
    %(NEWDATA)s<-rbind(%(NEWDATA)s, sData)
    }""" % opts, wantType = redR.NOCONVERSION)
        self.GUIOUTPUT_Text.clear()
        self.GUIOUTPUT_Text.insertPlainText(self.R('paste(capture.output(head(%(NEWDATA)s)), collapse ="\n")' % opts, wantType = redR.CONVERT))
        newData = signals.RDataFrame.RDataFrame(self, data = self.Rvariables['norm'])
        self.rSend("data", newData)
        
    