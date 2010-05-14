## Biopython interface that allows download of sequence info from the net

"""
<name>Get SwissProt Data</name>
<description>Retrieves data from a connection to SwissProt.</description>
<tags>Biopython</tags>
<icon>icons/readfile.png</icon>
<priority>10</priority>
"""

from Bio import ExPASy
from Bio import SeqIO
from OWRpy import *

class getSwissProtData(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "Get SwissProt Data", wantMainArea = 0, resizingEnabled = 1)
        
        self.outputs = [('Sequence List', signals.RedRBiopython.SequenceRecordCollection)]
        
        ### GUI ###
        
        # want to set the database, the type, and the id'self
        
        box = redRGUI.groupBox(self.controlArea, label = 'Parameters')
        # self.database = redRGUI.comboBox(box, label = 'Sequence Database:', items = ['nucleotide'], toolTip = 'Select the database that you would like your sequecne to come from')
        # self.type = redRGUI.comboBox(box, label = 'Sequence Type:', items = ['fasta', 'gb'], toolTip = 'Select the type of sequence that you would like to retrieve')
        self.id = redRGUI.lineEdit(box, label = 'ID\'s:', toolTip = 'List the ID\'s that you would like to retrieve, separated using a comma')
        self.infoA = redRGUI.widgetLabel(box, '')
        button = redRGUI.button(self.bottomAreaRight, 'Commit', callback = self.commit)
        
    def commit(self):
        self.infoA.clear()
        handle = ExPASy.get_sprot_raw(str(self.id.text()))
        try:
            records = SeqIO.to_dict(SeqIO.parse(handle, 'swiss'))
            handle.close()
        except Exception as inst:
            handle.close()
            print inst
            self.infoA.setText('Error occured, see output for details')
            return
        
        newData = signals.RedRBiopython.SequenceRecordCollection(data = records)
        self.rSend('Sequence List', newData)
