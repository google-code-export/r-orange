"""Linear Model widget

.. helpdoc::
Generates a linear model fit to data.
"""


"""<widgetXML>
    <name>
        Linear Model
    </name>
    <icon>
        defualt.png
    </icon>
    <summary>
        Generates a linear model fit to data.
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

class lm(OWRpy): 
    def __init__(self, **kwargs):
        OWRpy.__init__(self, wantGUIDialog = 1, **kwargs)
        
        """.. rrvnames::""" ## left blank so no description  
        self.setRvariableNames(["lm"])
        
        
        self.RFunctionParam_formula = ""
        self.RFunctionParam_data = ''
        self.modelFormula = ''
        self.processingComplete = 0
        
        """.. rrsignals::
            :description: `Input data table.`"""
        self.inputs.addInput('id0', 'data', signals.base.RDataFrame, self.processdata)
        
        """.. rrsignals::
            :description: `LM Fit object for further modeling.`"""
        self.outputs.addOutput('id0', 'lm Output', signals.stats.RLMFit)
        
        """.. rrsignals::
            :description: `LM Plot Attribute, for plotting.`"""
        self.outputs.addOutput('id1', 'lm plot attribute', signals.plotting.RPlotAttribute)

        
        #GUI
        
        box = redRGUI.base.widgetBox(self.GUIDialog, orientation = 'horizontal')
        paramBox = redRGUI.base.groupBox(self.GUIDialog, 'Parameters')
        formulaBox = redRGUI.base.widgetBox(self.controlArea)
        
        """.. rrgui::
            :description: `Subset parameter.`
        """
        self.RFunctionParam_subset = redRGUI.base.lineEdit(paramBox, 'NULL', label = "subset:")
        
        """.. rrgui::
            :description: `qr parameter.`
        """
        self.RFunctionParam_qr = redRGUI.base.lineEdit(paramBox, 'TRUE', label = "qr:")

        """.. rrgui::
            :description: `singular_ok parameter.`
        """
        self.RFunctionParam_singular_ok = redRGUI.base.lineEdit(paramBox, 'TRUE', label = "singular_ok:")
        
        """.. rrgui::
            :description: `y parameter.`
        """
        self.RFunctionParam_y = redRGUI.base.lineEdit(paramBox, 'FALSE', label = "y:")
        
        """.. rrgui::
            :description: `weights parameter.`
        """
        self.RFunctionParam_weights = redRGUI.base.lineEdit(paramBox, "", label = "weights:")
        
        """.. rrgui::
            :description: `offset parameter.`
        """
        self.RFunctionParam_offset = redRGUI.base.lineEdit(paramBox, "", label = "offset:")
        
        """.. rrgui::
            :description: `contrasts parameter.`
        """
        self.RFunctionParam_contrasts = redRGUI.base.lineEdit(paramBox, "NULL", label = "contrasts:")
        
        """.. rrgui::
            :description: `x parameter.`
        """
        self.RFunctionParam_x = redRGUI.base.lineEdit(paramBox, "FALSE", label = "x:")
        
        """.. rrgui::
            :description: `model parameter.`
        """
        self.RFunctionParam_model = redRGUI.base.lineEdit(paramBox, "TRUE", label = "model:")
        
        """.. rrgui::
            :description: `method parameter.`
        """
        self.RFunctionParam_method = redRGUI.base.lineEdit(paramBox, "qr", label = "method:")
        
        #start formula entry section

        buttonsBox = redRGUI.base.widgetBox(formulaBox, "Commands")
        
        """.. rrgui::
            :description: `Formula entry for model.`
        """
        self.formulEntry = redRGUI.base.RFormulaEntry(buttonsBox,label='Formula',displayLabel=False)
        
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        #self.processButton.setEnabled(False)
        self.status.setText('Data Not Connected Yet')
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            names = self.R('colnames('+self.RFunctionParam_data+')')
            self.formulEntry.update(names)
            self.status.setText('Data Connected')
            if self.commit.processOnInput():
                self.commitFunction()

        else:
            self.formulEntry.clear()
            self.RFunctionParam_data = ''
            self.status.setText('Data Connection Failed. Please Reconnect')
    def commitFunction(self):
        if self.RFunctionParam_data == '': 
            self.status.setText('No data')
            return
        if self.formulEntry.Formula()[0] == '' or self.formulEntry.Formula()[1] == '':
            self.status.setText('Please select valid formula parameters')
            return
        self.RFunctionParam_formula = self.formulEntry.Formula()[0] + ' ~ ' + self.formulEntry.Formula()[1]

        
        self.R(self.Rvariables['lm']+'<-lm(data='+unicode(self.RFunctionParam_data)+',subset='+unicode(self.RFunctionParam_subset.text())+',qr='+unicode(self.RFunctionParam_qr.text())+',formula='+unicode(self.RFunctionParam_formula)+',singular_ok='+unicode(self.RFunctionParam_singular_ok.text())+',y='+unicode(self.RFunctionParam_y.text())+',weights='+unicode(self.RFunctionParam_weights.text())+',offset='+unicode(self.RFunctionParam_offset.text())+',contrasts='+unicode(self.RFunctionParam_contrasts.text())+',x='+unicode(self.RFunctionParam_x.text())+',model='+unicode(self.RFunctionParam_model.text())+',method="'+unicode(self.RFunctionParam_method.text())+'")', wantType = 'NoConversion')
        newData = signals.stats.RLMFit(self, data = self.Rvariables['lm'])
        self.rSend("id0", newData)
        
        newPlotAtt = signals.plotting.RPlotAttribute(self, data = 'abline('+self.Rvariables['lm']+')')
        self.rSend("id1", newPlotAtt)
        
