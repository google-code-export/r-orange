"""
.. helpdoc::
<p>Some Red-R manipulations send RList objects through their send slots.  Lists are collections of other objects such as RVectors, RDataFrames, or even other RLists.  This widget simply shows the elements of your RList in it's 'List Data' Section.  Clicking on these sends just that section of the data through the appropriate slot in the List Selector's outputs.</p>
"""

"""
<widgetXML>    
    <name>List Selection</name>
    <icon>default.png</icon>
    <tags> 
        <tag>Subsetting</tag> 
    </tags>
    <summary>View all the elements of a list and select one to send forward.</summary>
    <citation>
    <!-- [REQUIRED] -->
        <author>
            <name>Red-R Core Team</name>
            <contact>http://www.red-r.org/contact</contact>
        </author>
        <reference>http://www.red-r.org</reference>
    </citation>
</widgetXML>
"""

"""
<name>List Selection</name>
<tags>Subsetting</tags>
"""

from OWRpy import *
import redRGUI, signals
import redRGUI

import redRi18n
_ = redRi18n.get_(package = 'base')
class ListSelector(OWRpy):
    globalSettingsList= ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        #self.selection = 0
        self.setRvariableNames(['listelement'])
        self.data = None
        
        self.inputs.addInput('id0', _('R List'), [signals.base.RList, signals.base.RArbitraryList] , self.process)

        self.outputs.addOutput('id0', _('R Data Frame'), signals.base.RDataFrame)
        self.outputs.addOutput('id1', _('R Vector'), signals.base.RVector)
        self.outputs.addOutput('id2', _('R List'), signals.base.RList)
        self.outputs.addOutput('id3', _('R Variable'), signals.base.RVariable)
        self.outputs.addOutput('id4', _('R Matrix'), signals.base.RMatrix)

        
        #GUI
        #box = redRGUI.base.groupBox(self.controlArea, "List Data")
        
        self.names = redRGUI.base.listBox(self.controlArea, label=_("List of Data"), displayLabel=True,
        callback = self.selectionChanged)
        self.infoa = redRGUI.base.widgetLabel(self.controlArea, '')
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.sendSelection,
        processOnChange=True, processOnInput=True)

        
    def process(self, data):
        self.data = None
        
        if data:
            self.data = data.getData()
            names = self.R('names('+self.data+')', wantType = 'list')
            print unicode(names)
            if names == None:
                names = range(1, self.R('length('+self.data+')')+1)
                print names
            self.names.update(names)
            if self.commit.processOnInput():
                self.sendSelection()
        else:
            self.names.clear()
            for signal in self.outputs.outputIDs():
                self.rSend(signal, None)
          
    def selectionChanged(self):
        if self.commit.processOnChange():
            self.sendSelection()
        
    def sendSelection(self):
        #print self.names.selectedItems()[0]
        if self.data == None: 
            self.status.setText('No data to process')
            return
        name = unicode(self.names.row(self.names.currentItem())+1)
        self.Rvariables['listelement'] = self.data+'[['+name+']]'
        # use signals converter in OWWidget to convert to the signals class
        myclass = self.R('class('+self.Rvariables['listelement']+')')
        print myclass
        if myclass == 'data.frame':
            
            newData = signals.base.RDataFrame(self, data = self.Rvariables['listelement'], parent = self.Rvariables['listelement'])
            self.rSend("id0", newData)
            #self.infoa.setText('Sent Data Frame')
            slot = 'Data Frame'
        elif myclass == 'list':
            newData = signals.base.RList(self, data = self.Rvariables['listelement'])
            self.rSend("id2", newData)
            #self.infoa.setText('Sent List')
            slot = 'List'
        elif myclass in ['vector', 'character', 'factor', 'logical', 'numeric', 'integer', ['POSIXt', 'POSIXct']]:
            newData = signals.base.RVector(self, data = self.Rvariables['listelement'])
            self.rSend("id1", newData)
            #self.infoa.setText('Sent Vector')
            slot = 'Vector'
        elif myclass in ['matrix']:
            newData = signals.base.RMatrix(self, data = self.Rvariables['listelement'])
            self.rSend("id4", newData)
            #self.infoa.setText('Sent Matrix')
            slot = 'Matrix'
        else:
            newData = signals.base.RVariable(self, data = self.Rvariables['listelement'])
            self.rSend("id3", newData)
            slot = 'R Variable'
        
        self.infoa.setText(_('Sent %(NAME)s as %(SLOT)s') % {'NAME':name, 'SLOT':slot})