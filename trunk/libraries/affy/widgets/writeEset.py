"""
<name>Write eSet</name>
<description>Writes an eSet to a tab delimited file.</description>
<tags>Microarray</tags>
<RFunctions>affy:write.exprs</RFunctions>
<icon>readcel.png</icon>
<priority>80</priority>
"""
from OWRpy import *
import redRGUI
## depricated may bring back later
    class writeEset(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Write Eset")
        
        self.data = None
        self.fileName = ""
        self.saveSettingsList.extend(['data', 'fileName'])
        
        self.inputs = [("Affybatch", signals.RVariable, self.nothingb)]
        self.outputs = None
        
        
        
        #GUI
        box = redRGUI.widgetBox(self.controlArea, "Write to file.")
        #redRGUI.lineEdit(box, label = "File Name", orientation = "horizontal") 
        writeButton = redRGUI.button(box, "Write to file", callback = self.write, width=200)
        self.infoa = redRGUI.widgetLabel(box, "No output yet")
        
    def nothingb(self,data):
        if data:
            self.data = data.getData()
        else: return
            
    def write(self):
        if not self.require_librarys(['affy']):
            self.status.setText('R Libraries Not Loaded.')
            return
        if self.data == None or self.data == '':
            self.infoa.setText("Data has not been loaded yet")
            return
        if ('HomeFolder' not in qApp.canvasDlg.settings.keys()):
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(qApp.canvasDlg.settings['saveSchemaDir']), "Plain Text (*.txt)"))
        else: 
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(qApp.canvasDlg.settings['HomeFolder']), "Plain Text (*.txt)"))

        self.R('write.exprs('+self.data+',file="'+file+'", sep="\t")')
        self.infoa.setText("Data was writen to "+file+" successfully!")
        self.notes.setCursorToEnd()
        self.notes.insertHtml('<br>File Saved as: '+file+'<br>')
        