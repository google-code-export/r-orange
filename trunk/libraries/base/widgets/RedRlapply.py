"""List Apply


.. helpdoc::
A transparent implementation of lapply (advanced).

This widget requires some knowlege about the function that the user wants to implement, and provides only a line exit to specify the function and parameters to be added.  All additional parameters should be indicated by the user.  The purpose of this widget is to allow advanced users to quickly apply functions over lists of data.  Should a novice user have a list of data, it might be better to subset the list using List Selection and then build a pipeline that can be itterated through by selecing different elements from the list.

"""


"""<widgetXML>
    <name>
        List Apply
    </name>
    <icon>
        default.png
    </icon>
    <summary>
        A transparent implementation of lapply (advanced).
    </summary>
    <tags>
        <tag priority="10">
            R
        </tag>
    </tags>
    <author>
        <authorname>Kyle R. Covington</authorname>
        <authorcontact>kyle@red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

from OWRpy import * 
import redRGUI, signals
import redRGUI

class RedRlapply(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_object = ''
        self.setRvariableNames(["lapply"])
        """.. rrsignals::
            :description: `A data table read in by the widget`"""
        self.inputs.addInput('id0', 'Data Table', signals.base.RList, self.processobject)
        self.outputs.addOutput('id1', 'Data List', signals.base.RList)
        
        self.guiparam_function = redRGUI.base.lineEdit(self.controlArea, label = "Function")
        self.guiparam_parameters = redRGUI.base.lineEdit(self.controlArea, label = "Parameters (optional)")
        
        
        """.. rrgui::
            :description: `Run the subsetting.`
        """
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
        self.RoutputWindow = redRGUI.base.textEdit(box,label='R Output', displayLabel=False)
        
    def processobject(self, data):
        if data:
            self.RFunctionParam_object=unicode(data.getData())
            if self.commit.processOnInput():
                self.commitFunction()
        else: self.RFunctionParam_object = ''
    def commitFunction(self):
        if self.RFunctionParam_object == '': return
        if self.guiparam_parameters.text() != '':
            self.R('%(new)s<-lapply(%(data)s, %(function)s, %(params)s)' % {'new':self.Rvariables['lapply'], 'data':self.RFunctionParam_object, 'function':self.guiparam_function.text(), 'params':self.guiparam_parameters.text()}, wantType = redR.NOCONVERSION)
        else:
            self.R('%(new)s<-lapply(%(data)s, %(function)s)' % {'new':self.Rvariables['lapply'], 'data':self.RFunctionParam_object, 'function':self.guiparam_function.text()}, wantType = redR.NOCONVERSION)
        
        newdata = signals.base.RList(self, data = self.Rvariables['lapply'])
        self.rSend('id1', newdata)
        
        self.RoutputWindow.clear()
        self.RoutputWindow.captureOutput(self.Rvariables['lapply'])

