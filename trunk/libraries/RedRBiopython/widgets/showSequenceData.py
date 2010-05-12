## Biopython interface tthat shows informaiton collected from sequence records accepts a sequence collection and allows the user to show informaiton about any one of the records.

"""
<name>Show Sequence Info</name>
<description></description>
<tags>Data Input, Biopython</tags>
<icon>icons/readfile.png</icon>
<priority>10</priority>
"""

from Bio import Entrez
from Bio import SeqIO
from OWRpy import *

class showSequenceData(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "Show Sequence Data", wantMainArea = 0, resizingEnabled = 1)
        
        self.data = None
        self.inputs = [('Sequence Collection', signals.RedRBiopython.SequenceRecordCollection, self.gotData)]
        
        ## GUI ##
        
        box = redRGUI.groupBox(self.controlArea, 'Sequence Info')
        
        ## combobox with sequence informaiton
        self.sequenceCombo = redRGUI.comboBox(box, label = 'Sequence Record:', toolTip = 'Select a sequence record to show the data from.', callback = self.showRecord)
        
        ## text area for sequence data ##
        
        self.sequenceTextArea = redRGUI.textEdit(box)
        
    def gotData(self, data):
        if data:
            self.data = data
            records = self.data.data.keys()
            self.sequenceCombo.update(records)
        else:
            self.sequenceCombo.clear()
            self.sequenceTextArea.clear()
            
    def showRecord(self):
        # move through the records and if they match the selected one then you can show the data and return
        
        wantRecord = str(self.sequenceCombo.currentText())
        
        rec = self.data.data[wantRecord]
        
        self.sequenceTextArea.insertPlainText('ID: '+str(rec.id)+'\n')
        self.sequenceTextArea.insertPlainText('Name:'+str(rec.name)+'\n')
        self.sequenceTextArea.insertPlainText('Sequence:'+str(rec.seq)+'\n')
        self.sequenceTextArea.insertPlainText('Description:'+str(rec.description)+'\n')
        self.sequenceTextArea.insertPlainText('Letter Annotations:'+str(rec.letter_annotations)+'\n')
        self.sequenceTextArea.insertPlainText('Annotations:'+str(rec.annotations)+'\n')
        self.sequenceTextArea.insertPlainText('Features:'+str(rec.features)+'\n')
        #self.sequenceTextArea.insertPlainText(str(rec.id))
        return
        