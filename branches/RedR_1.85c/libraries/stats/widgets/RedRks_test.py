"""Kolmogorov-Smirnov


.. helpdoc::
The Kolmogorov-Smirnov test compares the null distribution with the empirical distribution function of the observed data, where left truncated data samples are allowed. The test statistic is given by

KS+ = sqrt(n)/(1-zH) sup(zH + j/n (1-zH) -zj)

KS+ = sqrt(n)/(1-zH) sup(zj - (zH + (j-1)/n (1-zH)))

KS = max(KS+, KS-)

with z_H = F_theta(H) and z_j=F_theta(x_j), where x_1, ..., x_n are the ordered data values. Here, F_theta is the null distribution.
"""


"""<widgetXML>
    <name>Kolmogorov-Smirnov</name>
    <icon>default.png</icon>
    <summary>Kolmogorov-Smirnov test providing a comparison of a fitted distribution with the empirical distribution.</summary>
    <tags>
        <tag priority="10">
            Distributions
        </tag>
    </tags>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

"""
<name>ks.test</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>stats:ks.test</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class RedRks_test(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
            OWRpy.__init__(self, **kwargs)
            self.setRvariableNames(["ks.test"])
            self.data = {}
            self.RFunctionParam_y = ''
            self.RFunctionParam_x = ''
            
            """.. rrsignals::
            :description: `X vector`"""
            self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)
            
            """.. rrsignals::
            :description: `Y vector`"""
            self.inputs.addInput('id0', 'y', signals.base.RVector, self.processy)
            
            

            
            self.RFunctionParamalternative_comboBox = redRGUI.base.comboBox(self.controlArea, label = "alternative:", items = ["two.sided","less","greater"])
            self.RFunctionParamexact_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "exact:", text = 'NULL')
            redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
            self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "RoutputWindow")
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
            if unicode(self.RFunctionParam_y) == '': 
                self.status.setText('No Y data')
                return
            if unicode(self.RFunctionParam_x) == '': 
                self.status.setText('No X data')
                return
            injection = []
            string = 'alternative=\''+unicode(self.RFunctionParamalternative_comboBox.currentText())+'\''
            injection.append(string)
            if unicode(self.RFunctionParamexact_lineEdit.text()) != '':
                    string = 'exact='+unicode(self.RFunctionParamexact_lineEdit.text())+''
                    injection.append(string)
            inj = ','.join(injection)
            self.R(self.Rvariables['ks.test']+'<-ks.test(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+','+inj+')')
            self.R('txt<-capture.output('+self.Rvariables['ks.test']+')')
            self.RoutputWindow.clear()
            tmp = self.R('paste(txt, collapse ="\n")')
            self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
