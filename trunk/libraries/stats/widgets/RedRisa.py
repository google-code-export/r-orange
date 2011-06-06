"""ISA widget

This widget reads in text files from either a delimited file or the clipboard.  Clipboard files are typically space separated so values with spaces in the strings should be adjusted.

.. helpdoc::
For the impatient
The easiest way to run ISA is to call the isa function with your input matrix as the single argument.
This does all steps of a typical ISA work ﬂow, with the default parameters.

ISA biclusters

An ISA module is pair; a subset of the rows of the input matrix and a subset of its columns. In other
words, a bicluster is a block of the reordered input matrix, where reordering means a permutation of
both the rows and columns. (Another bicluster might be block of the same permuted input matrix
or one after a different permutation.)
The criteria of a good bicluster is that 1) its rows are signiﬁcantly different than the other rows, when
we consider only the positions deﬁned by the columns of the same bicluster, and (symmetrically) 2)
its columns are signiﬁcantly different than the other columns, when we consider only the positions
deﬁned by the rows of the same bicluster.
In other words, the rows of the bicluster are correlated, but only on the columns deﬁned by the same
bicluster; and the opposite is also true, the columns of the bicluster are correlated, but only on the
rows deﬁned by the same bicluster.
ISA biclusters are soft, two biclusters may overlap in their rows, columns or even both. It is also
possible that some rows and/or columns of the input matrix are not found to be part of any ISA
biclusters. Depending on the stringency parameters, it might even happen that ISA does not ﬁnd
any biclusters.

    ISA row and column scores

    ISA biclusters are not only soft, but every row and column in a given bicluster has a score, a number
between minus one and one. The further this number is from zero, then stronger is the association
of the given row or column to the bicluster.
"""


"""<widgetXML>
    <name>Iterative Signature Algorithm</name>
    <icon>default.png</icon>
    <summary>Run ISA with the default parameters</summary>
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
<name>isa</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>isa2:isa</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
class RedRisa(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["isa"])
        self.data = {}
        self.RFunctionParam_data = ''
        
        """.. rrsignals::
            :description: `Input data.`"""
        self.inputs.addInput('id0', 'data', signals.base.RMatrix, self.processdata)

        """.. rrsignals::
            :description: `ISA Output model.`"""
        self.outputs.addOutput('id0', 'isa Output', signals.base.RModelFit)


        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processdata(self, data):
        self.require_librarys(["isa2"])
        if data:
            self.RFunctionParam_data=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': return
        
        self.R(self.Rvariables['isa']+'<-isa(data='+unicode(self.RFunctionParam_data)+')')
        newData = signals.base.RModelFit(self, data = self.Rvariables["isa"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
