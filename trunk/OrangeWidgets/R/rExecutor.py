"""
<name>R Executor</name>
<description>Accepts and sends R objects as well as performing R commands</description>
<icon>icons/RExecutor.PNG</icon>
<priority>80</priority>
"""

from OWRpy import *
import OWGUI
from rpy_options import set_options
set_options(RHOME=os.environ['RPATH'])
from rpy import *

class rExecutor(OWRpy):
    settingsList = ['command', 'sendthis', 'sendt']
    def __init__(self, parent=None, signalManager=None):
        #OWWidget.__init__(self, parent, signalManager, "Sample Data")
        OWRpy.__init__(self)
        
        self.command = ''
        self.sendthis = ''
        self.sendt = {}
        self.dfselected = None
        self.loadSettings()
        
        self.inputs = [('R.object', RvarClasses.RVariable, self.process)]
        self.outputs = [('R.object', RvarClasses.RVariable), ('R Data Frame', RvarClasses.RDataFrame), ('R List', RvarClasses.RList), ('R Vector', RvarClasses.RVector)]
        
        
        
        #GUI
        self.box = OWGUI.widgetBox(self.controlArea, "R Commander")
        self.infob = OWGUI.widgetLabel(self.box, "")
        
        
        varbutton = OWGUI.button(self.box, self, "Recieved", callback = self.putrecieved, width = 150)
        history = OWGUI.button(self.box, self, "RHistory", callback = self.putRHistory, width = 150)
        self.infoa = OWGUI.widgetLabel(self.box, "")
        
        self.dataBox = OWGUI.widgetBox(self.controlArea, "Input Infromation")
        self.infov = OWGUI.widgetLabel(self.dataBox, "No Input")
        
        self.metadataBox = OWGUI.widgetBox(self.controlArea, "Metadata")
        self.infoM = OWGUI.widgetLabel(self.metadataBox, "No Meta Data")
        self.metadataLB = OWGUI.listBox(self.metadataBox, self, callback = self.insertMetaDataVar)
        
        
        # splice canvas for the right hand side of the canvas
        self.splitCanvas = QSplitter(Qt.Vertical, self.mainArea)
        self.mainArea.layout().addWidget(self.splitCanvas)
        
        runbox = OWGUI.widgetBox(self, "Commander")
        self.splitCanvas.addWidget(runbox)
        OWGUI.lineEdit(runbox, self, "command", "R Command", orientation = 'horizontal')
        processbutton = OWGUI.button(runbox, self, "Run", callback = self.runR, width=150)
        
        self.thistext = QTextEdit(self)
        self.splitCanvas.addWidget(self.thistext)
        
        
        
        sendbox = OWGUI.widgetBox(self.controlArea, "Send Box")
        OWGUI.lineEdit(sendbox, self, "sendthis", "Send", orientation = 'horizontal')
        sendbutton = OWGUI.button(sendbox, self, "Send", callback =self.sendThis, width=150)
        self.resize(800,600)
        
    def putrecieved(self):
        self.command = str(self.data)
        
    def insertMetaDataVar(self):
        tmp = str(self.olddata[str(self.metadataLB.selectedItems()[0].text())])
        self.infoM.setText(tmp)
        self.command = tmp
    def sendThis(self):
        self.sendt = {'data':self.sendthis}
        thisdata = self.sendt['data']
        thisdataclass = self.rsession('class('+thisdata+')')
        if thisdataclass.__class__.__name__ == 'list': #this is a special R type so just send as generic
            self.rSend('R.object', self.sendt)
        elif thisdataclass.__class__.__name__ == 'str':
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                self.rSend('R Vector', self.sendt)
            elif thisdataclass == 'character': #we have a character vector as the object
                self.rSend('R Vector', self.sendt)
            elif thisdataclass == 'data.frame': # the object is a data.frame
                self.rSend('R Data Frame', self.sendt)
            elif thisdataclass == 'matrix': # the object is a matrix
                self.rSend('R Data Frame', self.sendt)
            elif thisdataclass == 'list': # the object is a list
                self.rSend('R List', self.sendt)
            else:    # the data is of a non-normal type send anyway as generic
                self.rSend('R.object', self.sendt)
        else:
            self.rSend('R.object', self.sendt)
    def runR(self):
        self.rsession('txt<-capture.output('+self.command+')')
        pasted = self.rsession('paste(txt, collapse = " \n")')
        self.thistext.insertPlainText('>>>'+self.command+'##Done')
        self.thistext.insertHtml('<br><pre>'+pasted+'<\pre><br>')
    
    def putRHistory(self):
        self.thistext.clear()
        self.thistext.insertHtml(OWRpy.Rhistory)
    def process(self, data):
        if data:
            self.data = str(data['data'])
            self.olddata = data
            for key in self.olddata.keys():
                self.metadataLB.addItem(key)
            self.infob.setText(self.data)
            # logic to handle assignment of the data elements
            thisclass = self.rsession('class('+self.data+')')
            #are there multipe classes for this object?
            if thisclass.__class__.__name__ == 'str': #there is only one class for this object in R
                if thisclass == 'numeric': # we have a numeric vector as the object
                    self.isNumeric()
                elif thisclass == 'character': #we have a character vector as the object
                    self.isCharacter()
                elif thisclass == 'data.frame': # the object is a data.frame
                    self.isDataFrame()
                elif thisclass == 'matrix': # the object is a matrix
                    self.isMatrix()
                elif thisclass == 'list': # the object is a list
                    self.isList()
                else:
                    self.infov.setText("R object is of non-standard type.")
            if thisclass.__class__.__name__ == 'list': # we need to handle multible classes 
                for item in thisclass:
                    if item == 'numeric': # we have a numeric vector as the object
                        self.isNumeric()
                    elif item == 'character': #we have a character vector as the object
                        self.isCharacter()
                    elif item == 'data.frame': # the object is a data.frame
                        self.isDataFrame()
                    elif item == 'matrix': # the object is a matrix
                        self.isMatrix()
                    elif item == 'list': # the object is a list
                        self.isList()
                    else:
                        self.infov.setText("R object is of non-standard type.")
                    
        else: return
    
    def isNumeric(self):
        self.infov.setText("Numeric Vector Connected of length %s" % str(self.rsession('length('+self.data+')')))
    def isCharacter(self):
        self.infov.setText("Character Vector Connected of length %s" % str(self.rsession('length('+self.data+')')))
    def isDataFrame(self):
        self.infov.setText("Data Frame Connected with %s columns" % str(self.rsession('length('+self.data+')')))
        colnames = self.rsession('colnames('+self.data+')')
        if colnames != 'NULL' and self.dfselected == None:
            self.dfselected = OWGUI.listBox(self.dataBox, self)
            for e in colnames:
                self.dfselected.addItem(e)
        elif colnames != 'NULL' and self.dfselected != None:
            self.dfselected.clear()
            for e in colnames:
                self.dfselected.addItem(e)
    def isMatrix(self):
        self.infov.setText("Matrix connected with %s elements and %s columns" % (str(self.rsession('length('+self.data+')')), str(self.rsession('length('+self.data+'[1,])'))))
        colnames = self.rsession('colnames('+self.data+')')
        if colnames != 'NULL' and colnames != '' and colnames != 'None':
            self.dfselected = OWGUI.listBox(self.dataBox, self)
            for e in colnames:
                self.dfselected.addItem(e)
    def isList(self):
        self.infov.setText("List object connected with %s elements" % str(self.rsession('length('+self.data+')')))
        
        