"""Subset to List


.. helpdoc::
This widget performs subsetting into a list structure where each level of the list represents a subsetting of the data table by the selected index. 

For example, the data frame;

a       b       c       
'a'     7       8
'a'     8       9
'b'     8       9
'b'     30      49

Becomes;
$a
a       b       c       
'a'     7       8
'a'     8       9

$b
a       b       c       
'b'     8       9
'b'     30      49

"""


"""<widgetXML>
    <name>
        Subset to List
    </name>
    <icon>
        default.png
    </icon>
    <summary>
        Subset a data table into several tables in a list.
    </summary>
    <tags>
        <tag priority="10">
            Advanced Stats
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

class subtolist(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_object = ''
        self.setRvariableNames(["sublist"])
        """.. rrsignals::
            :description: `A data table read in by the widget`"""
        self.inputs.addInput('id0', 'Data Table', signals.base.RDataFrame, self.processobject)
        self.outputs.addOutput('id1', 'Data List', signals.base.RList)
        
        
        self.selectBox = redRGUI.base.comboBox(self.controlArea, label = "Subset Column", callback = self.commitFunction)
        
        #box = redRGUI.base.groupBox(self.controlArea, "Output")
        
        """.. rrgui::
            :description: `Run the subsetting.`
        """
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
        #self.RoutputWindow = redRGUI.base.textEdit(box,label='R Output', displayLabel=False)
        
        self.R(
"""subtolist<-function(data, index){
	# purpose is to turn the data.frame into a list with levels the same as the levels of the indicated index.
	if(class(data) != "data.frame"){ return(NULL) }
    if(! index %in% names(data)){ return(NULL) } 
	newdata <- list()
	for (i in levels(as.factor(data[,index]))){
		newdata[[i]]<-data[data[,index] == i,]
	}
	return(newdata)
}
""", wantType = redR.NOCONVERSION)
        
    def processobject(self, data):
        if data:
            self.RFunctionParam_object=unicode(data.getData())
            if self.commit.processOnInput():
                self.commitFunction()
        else: self.RFunctionParam_object = ''
    def commitFunction(self):
        if self.RFunctionParam_object == '': return
        self.R('%(new)s<-subtolist(%(data)s, %(index)s)' % {'new':self.Rvariables['sublist'], 'data':self.RFunctionParam_object, 'index':self.selectBox.currentId()}, wantType = redR.NOCONVERSION)
        if not self.R(self.Rvariables['sublist']):
            self.status.setText('Subsetting failed, please check selections')
            return
        newdata = signals.base.RList(self, data = self.Rvariables['sublist'])
        self.rSend('id1', newdata)

