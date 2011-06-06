"""ANOVA-LM widget

.. helpdoc::
Performs LM then ANOVA function on a model fit or data.
"""


"""<widgetXML>
    <name>
        ANOVA-LM
    </name>
    <icon>
        defualt.png
    </icon>
    <summary>
        Read data files into Red-R.
    </summary>
    <tags>
        <tag priority="50">
            Parametric
        </tag>
    </tags>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

"""
<name>ANOVA-LM</name>
<tags>Parametric</tags>
<icon>stats.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI

class anova_lm(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_object = ''
        self.saveSettingsList.extend(['RFunctionParam_object'])
        
        """.. rrsignals::
            :description: `A linear model fit.`"""
        self.inputs.addInput('id0', 'object', signals.stats.RLMFit, self.processobject)

        
        box = redRGUI.base.groupBox(self.controlArea, "Output")
        
        """.. rrgui::
            :description: `Run the ANOVA LM function.`
        """
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
        """.. rrgui::
            :description: `Display output from the ANOVALM function.`
        """
        self.RoutputWindow = redRGUI.base.textEdit(box,label='R Output', displayLabel=False)
        
    def onLoadSavedSession(self):
        self.commitFunction()
        
    def processobject(self, data):
        if data:
            self.RFunctionParam_object=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
        else: self.RFunctionParam_object = ''
    def commitFunction(self):
        if self.RFunctionParam_object == '': return
        self.R('txt<-capture.output('+'anova.lm(object='+unicode(self.RFunctionParam_object)+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp)

