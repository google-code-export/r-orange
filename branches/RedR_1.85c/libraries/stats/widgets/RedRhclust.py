"""Read File widget

.. helpdoc::
Performs a variety of clustering functions on a matrix of data.  Data can be connected in the RDataFrame form but should contain only numeric data.  If not then an error may be reported or the widget may not function as anticipated.  Please see the R help for the function hclust or a statistics text on clustering for more information on different clustering methods.
"""


"""<widgetXML>
    <name>Hierarchical Clustering</name>
    <icon>RedRhclust.png</icon>
    <summary>Performs a variety of clustering functions on a matrix of data.  Data can be connected in the RDataFrame form but should contain only numeric data.  If not then an error may be reported or the widget may not function as anticipated.  Please see the R help for the function hclust or a statistics text on clustering for more information on different clustering methods.</summary>
    <tags>
        <tag priority="10">
            Advanced Stats
        </tag>
    </tags>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

"""
<name>Hierarchical Clustering</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs a variety of clustering functions on a matrix of data.  Data can be connected in the RDataFrame form but should contain only numeric data.  If not then an error may be reported or the widget may not function as anticipated.  Please see the R help for the function hclust or a statistics text on clustering for more information on different clustering methods.</description>
<RFunctions>stats:hclust</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class RedRhclust(OWRpy): 
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        """.. rrvnames::""" ## left blank so no description     
        self.setRvariableNames(["hclust"])
        self.data = {}
        self.RFunctionParam_d = ''
        
        """.. rrsignals::
            :description: `A data table`"""
        self.inputs.addInput('id0', 'Data', signals.base.RDataFrame, self.processd)

        """.. rrsignals::
            :description: `HClust model fit`"""
        self.outputs.addOutput('id0', 'hclust Output', signals.base.RList)

        """.. rrgui::
            :description: `Cluster Method.`
        """
        self.RFunctionParammethod_comboBox = redRGUI.base.comboBox(self.controlArea, label = "Cluster Method:", items = ["complete","ward","single","average","mcquitty","centroid"])
        
        """.. rrgui::
            :description: `Dist Method.`
        """
        self.RFunctionParamdistmethod_comboBox = redRGUI.base.comboBox(self.controlArea, label = 'Dist Method:', items = ["euclidean", "maximum", "manhattan", "canberra", "binary", "minkowski"])
        
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processd(self, data):
        if data:
            self.RFunctionParam_d=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_d=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_d) == '': 
            self.status.setText('No data to process')
            return
        injection = []
        string = 'method=\''+unicode(self.RFunctionParammethod_comboBox.currentText())+'\''
        injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['hclust']+'<-hclust(d=dist(x='+unicode(self.RFunctionParam_d)+', method = \''+unicode(self.RFunctionParamdistmethod_comboBox.currentText())+'\'),'+inj+')')
        newData = signals.base.RList(self, data = self.Rvariables["hclust"], checkVal = False) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
