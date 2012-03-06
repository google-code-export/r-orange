"""Read File widget

This widget reads in text files from either a delimited file or the clipboard.  Clipboard files are typically space separated so values with spaces in the strings should be adjusted.

.. helpdoc::
Assessment of the clusterwise stability of a clustering of data, which can be cases*variables or dissimilarity data. The data is resampled using several schemes (bootstrap, subsetting, jittering, replacement of points by noise) and the Jaccard similarities of the original clusters to the most similar clusters in the resampled data are computed. The mean over these similarities is used as an index of the stability of a cluster (other statistics can be computed as well). The methods are described in Hennig (2007).

clusterboot is an integrated function that computes the clustering as well, using interface functions for various clustering methods implemented in R (several interface functions are provided, but you can implement further ones for your favourite clustering method). See the documentation of the input parameter clustermethod below.

Quite general clustering methods are possible, i.e. methods estimating or fixing the number of clusters, methods producing overlapping clusters or not assigning all cases to clusters (but declaring them as "noise"). Fuzzy clusterings cannot be processed and have to be transformed to crisp clusterings by the interface function.
"""


"""<widgetXML>
    <name>Cluster Boot</name>
    <icon>default.png</icon>
    <summary>
        Clusterwise cluster stability assessment by resampling
    </summary>
    <tags>
        <tag priority="10">
            Data Input
        </tag>
    </tags>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

"""
<name>clusterboot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>fpc:clusterboot</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals

class RedRclusterboot(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        """.. rrvnames::""" ## left blank so no description      
        self.setRvariableNames(["clusterboot"])
        self.data = {}
        self.require_librarys(["fpc"])
        self.RFunctionParam_data = ''
        
        """.. rrsignals::
            :description: `Data matrix input on which to model.`"""
        self.inputs.addInput("data", "data", signals.base.RMatrix, self.processdata)
        
        """.. rrsignals::
            :description: `Output list of clustering stability.`"""
        self.outputs.addOutput("clusterboot Output","clusterboot Output", signals.base.RArbitraryList)
        
        """.. rrgui::
            :description: `Distances parameter.`
        """
        self.RFunctionParamdistances_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "distances:", text = '')
        
        """.. rrgui::
            :description: `B parameter.`
        """
        self.RFunctionParamB_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "B:", text = '100')
        
        """.. rrgui::
            :description: `Jitter tuning parameter.`
        """
        self.RFunctionParamjittertuning_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "jittertuning:", text = '0.05')
        
        """.. rrgui::
            :description: `Clustering method.`
        """
        self.RFunctionParamclustermethod_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "clustermethod:", text = '')
        
        """.. rrgui::
            :description: `Dissolution method.`
        """
        self.RFunctionParamdissolution_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "dissolution:", text = '0.5')
        
        """.. rrgui::
            :description: `Multiple boot option.`
        """
        self.RFunctionParammultipleboot_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "multipleboot:", text = 'TRUE')
        
        """.. rrgui::
            :description: `bscompare parameter.`
        """
        self.RFunctionParambscompare_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "bscompare:", text = 'FALSE')
        
        """.. rrgui::
            :description: `showplots parameter.`
        """
        self.RFunctionParamshowplots_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "showplots:", text = 'FALSE')
        
        """.. rrgui::
            :description: `noisetuning parameter.`
        """
        self.RFunctionParamnoisetuning_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "noisetuning:", text = '0.0')
        
        """.. rrgui::
            :description: `bootmethod parameter.`
        """
        self.RFunctionParambootmethod_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "bootmethod:", text = '')
        
        """.. rrgui::
            :description: `recover parameter.`
        """
        self.RFunctionParamrecover_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "recover:", text = '0.75')
        
        """.. rrgui::
            :description: `subtuning parameter.`
        """
        self.RFunctionParamsubtuning_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "subtuning:", text = '')
        
        """.. rrgui::
            :description: `seed parameter to get the same results in random number generation.`
        """
        self.RFunctionParamseed_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "seed:", text = 'NULL')
        
        """.. rrgui::
            :description: `noisemethod parameter.`
        """
        self.RFunctionParamnoisemethod_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "noisemethod:", text = 'FALSE')
        
        
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):

        if data:
            self.RFunctionParam_data=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': return
        injection = []
        if unicode(self.RFunctionParamdistances_lineEdit.text()) != '':
            string = ',distances='+unicode(self.RFunctionParamdistances_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamB_lineEdit.text()) != '':
            string = ',B='+unicode(self.RFunctionParamB_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamjittertuning_lineEdit.text()) != '':
            string = ',jittertuning='+unicode(self.RFunctionParamjittertuning_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamclustermethod_lineEdit.text()) != '':
            string = ',clustermethod='+unicode(self.RFunctionParamclustermethod_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamdissolution_lineEdit.text()) != '':
            string = ',dissolution='+unicode(self.RFunctionParamdissolution_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParammultipleboot_lineEdit.text()) != '':
            string = ',multipleboot='+unicode(self.RFunctionParammultipleboot_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParambscompare_lineEdit.text()) != '':
            string = ',bscompare='+unicode(self.RFunctionParambscompare_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamshowplots_lineEdit.text()) != '':
            string = ',showplots='+unicode(self.RFunctionParamshowplots_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamnoisetuning_lineEdit.text()) != '':
            string = ',noisetuning='+unicode(self.RFunctionParamnoisetuning_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParambootmethod_lineEdit.text()) != '':
            string = ',bootmethod='+unicode(self.RFunctionParambootmethod_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamrecover_lineEdit.text()) != '':
            string = ',recover='+unicode(self.RFunctionParamrecover_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamsubtuning_lineEdit.text()) != '':
            string = ',subtuning='+unicode(self.RFunctionParamsubtuning_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamseed_lineEdit.text()) != '':
            string = ',seed='+unicode(self.RFunctionParamseed_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamnoisemethod_lineEdit.text()) != '':
            string = ',noisemethod='+unicode(self.RFunctionParamnoisemethod_lineEdit.text())+''
            injection.append(string)
        inj = ''.join(injection)
        self.R(self.Rvariables['clusterboot']+'<-clusterboot(data='+unicode(self.RFunctionParam_data)+inj+')')
        newData = signals.base.RArbitraryList(self, data = self.Rvariables["clusterboot"], checkVal = False) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("clusterboot Output", newData)