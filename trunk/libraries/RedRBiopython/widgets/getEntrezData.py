## Biopython interface that allows download of sequence info from the net

"""
<name>Get Entrez Data</name>
<description>Retrieves data from a connection to Entrez.</description>
<tags>Data Input, Biopython</tags>
<icon>icons/readfile.png</icon>
<priority>10</priority>
"""

from Bio import Entrez
from Bio import SeqIO
from OWRpy import *

class getEntrezData(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "SQLite Quert", wantMainArea = 0, resizingEnabled = 1)
        
        self.outputs = [('Sequence List', signals.RedRBiopython.SequenceRecordCollection)]
        self.loadSettings()
        ### GUI ###
        
        # want to set the database, the type, and the id'self
        
        box = redRGUI.groupBox(self.controlArea, label = 'Parameters')
        self.database = redRGUI.comboBox(box, label = 'Sequence Database:', items = ['nucleotide'], toolTip = 'Select the database that you would like your sequecne to come from')
        self.type = redRGUI.comboBox(box, label = 'Sequence Type:', items = ['fasta', 'gb'], toolTip = 'Select the type of sequence that you would like to retrieve')
        self.id = redRGUI.lineEdit(box, label = 'ID\'s:', toolTip = 'List the ID\'s that you would like to retrieve, separated using a comma')
        button = redRGUI.button(self.bottomAreaRight, 'Commit', callback = self.commit)
        
    def commit(self):
        handle = Entrez.efetch(db = str(self.database.currentText()), rettype = str(self.type.currentText()), id = str(self.id.text()))
        records = SeqIO.parse(handle, str(self.type.currentText()))
        handle.close()
        
        newData = signals.RedRBiopython.SequenceRecordCollection(data = records)
        self.rSend('Sequence List', newData)
