"""Test For Correlation (Single) widget

.. helpdoc::
Performs a test for correlation using the cor.test function.  This will make a test for correlation with associated summaries about the correlation including R-squared, p-value, etc.
"""


"""<widgetXML>
    <name>
        Test For Correlation (Single)
    </name>
    <icon>
        default.png
    </icon>
    <summary>
        Read data files into Red-R.
    </summary>
    <tags>
        <tag priority="10">
            Parametric
        </tag>
    </tags>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

from OWRpy import * 
import redRGUI, signals
import redRGUI 
class cor_test(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        """.. rrvnames::""" ## left blank so no description
        self.setRvariableNames(["cor.test"])
        self.data = {}
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        
        """.. rrsignals::
            :description: `X Vector`"""
        self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)
        
        """.. rrsignals::
            :description: `Y Vector`"""
        self.inputs.addInput('id0', 'y', signals.base.RVector, self.processy)
        
        
        """.. rrgui::
            :description: `Run the correlation test.`""" 
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        
        """.. rrgui::
            :description: `View the output of the correlation test.`""" 
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "RoutputWindow")
        
        """.. rrgui::
            :description: `Specify the method by which to compute the statistics`"""
        self.methodSelect = redRGUI.base.comboBox(self.controlArea, label = 'Method', items = [("pearson", "Pearson"), ("kendall", "Kendall"), ("spearman", "Spearman")])
    def processy(self, data):
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if unicode(self.RFunctionParam_x) == '': return
        injection = []
        injection.append('method = "%s"' % self.methodSelect.currentId())
        inj = ','.join(injection)
        self.R(self.Rvariables['cor.test']+'<-cor.test(y=as.numeric(as.character('+unicode(self.RFunctionParam_y)+')),x=as.numeric(as.character('+unicode(self.RFunctionParam_x)+')),'+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['cor.test']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)
