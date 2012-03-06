"""Fisher Exact Test widget

This widget reads in text files from either a delimited file or the clipboard.  Clipboard files are typically space separated so values with spaces in the strings should be adjusted.

.. helpdoc::
This widget will read data from tab, comma, or space delimited text files. On Microsoft Windows it will also ready Excel files. Click the browse button to search your computer for the file to read. Select how the columns are delimited. On data read or change in these options, the first few lines of the file will be scanned. R will try to automaticlly determine the type of the column. The column data types can be changed. Once the data, column and row header information is properly selected click Load Data to read the full file into Red-R and send forward.
"""


"""<widgetXML>
    <name>
        Fisher Exact Test
    </name>
    <icon>
        default.png
    </icon>
    <summary>
        Perform Fisher Exact Test on data.
    </summary>
    <tags>
        <tag priority="10">
            Stats
        </tag>
    </tags>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

"""
<name>Fisher Exact Test</name>
<tags>Stats</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 


class RedRfisher_test(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["fisher.test"])
        self.data = {}
        self.RFunctionParam_x = ''
        
        """.. rrsignals::
            :description: `Data matrix`"""
        self.inputs.addInput('id0', 'x', signals.base.RMatrix, self.processx)

        """.. rrgui::
            :description: `Number of Replicates for Monte Carlo.`
        """
        self.RFunctionParamB_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "Number of Replicates for Monte Carlo:", text = '2000')
        
        """.. rrgui::
            :description: `Hybrid Probabilities.`
        """
        self.RFunctionParamhybrid_checkBox = redRGUI.base.checkBox(self.controlArea, label = "Hybrid Probabilities:", buttons = ['FALSE', 'TRUE'], setChecked = 'FALSE')
        
        
        """.. rrgui::
            :description: `simulate_p_value.`
        """
        self.RFunctionParamsimulate_p_value_lineEdit = redRGUI.base.checkBox(self.controlArea, label = "simulate_p_value:", buttons = ['FALSE,TRUE'], setChecked = 'FALSE')
        
        """.. rrgui::
            :description: `Confidence Level.`
        """
        self.RFunctionParamconf_level_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "Confidence Level:", text = '0.95')
        
        """.. rrgui::
            :description: `Calculate Confidence Interval.`
        """
        self.RFunctionParamconf_int_lineEdit = redRGUI.base.checkBox(self.controlArea, label = "Calculate Confidence Interval:", buttons = ['TRUE','FALSE'], setChecked = 'TRUE')
        
        """.. rrgui::
            :description: `Alternative Hypothesis.`
        """
        self.RFunctionParamalternative_comboBox = redRGUI.base.comboBox(self.controlArea, label = "Alternative Hypothesis:", items = ["two.sided","greater","less"])
        
        """.. rrgui::
            :description: `Odds Ratio.`
        """
        self.RFunctionParamor_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "Odds Ratio:", text = '1')
        
        """.. rrgui::
            :description: `Run the comparison.`
        """
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,processOnInput=True)
        
        """.. rrgui::
            :description: `Display the data from the fitting.`
        """
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "R Output Window")
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': return
        injection = []
        # if unicode(self.RFunctionParamcontrol_lineEdit.text()) != '':
            # string = 'control='+unicode(self.RFunctionParamcontrol_lineEdit.text())+''
            # injection.append(string)
        if unicode(self.RFunctionParamB_lineEdit.text()) != '':
            string = 'B='+unicode(self.RFunctionParamB_lineEdit.text())+''
            injection.append(string)
        injection.append('hybrid ='+ unicode(self.RFunctionParamhybrid_checkBox.getChecked()))
        injection.append('simulate.p.value='+unicode(self.RFunctionParamsimulate_p_value_lineEdit.getChecked()))
        if unicode(self.RFunctionParamconf_level_lineEdit.text()) != '':
            string = 'conf.level='+unicode(self.RFunctionParamconf_level_lineEdit.text())+''
            injection.append(string)
        injection.append('conf.int='+unicode(self.RFunctionParamconf_int_lineEdit.text()))
        string = 'alternative='+unicode(self.RFunctionParamalternative_comboBox.currentText())+''
        injection.append(string)
        if unicode(self.RFunctionParamor_lineEdit.text()) != '':
            string = 'or='+unicode(self.RFunctionParamor_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['fisher.test']+'<-fisher.test(x='+unicode(self.RFunctionParam_x)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['fisher.test']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
