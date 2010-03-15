"""
<name>R Executor</name>
<description>Accepts and sends R objects as well as performing R commands</description>
<tags>Special, R</tags>
<icon>icons/RExecutor.PNG</icon>
<priority>80</priority>
"""

from OWRpy import *
import redRGUI

class rExecutor(OWRpy):
    settingsList = ['command', 'sendthis', 'sendt']
    def __init__(self, parent=None, signalManager=None):
        #OWWidget.__init__(self, parent, signalManager, "Sample Data")
        OWRpy.__init__(self, wantGUIDialog = 1, wandMainArea = 0)
        
        self.command = ''
        self.sendthis = ''
        self.sendt = {}
        self.dfselected = None
        self.loadSettings()
        
        self.inputs = [('R.object', RvarClasses.RVariable, self.process)]
        self.outputs = [('R.object', RvarClasses.RVariable), ('R Data Frame', RvarClasses.RDataFrame), ('R List', RvarClasses.RList), ('R Vector', RvarClasses.RVector)]
        #self.breakme()
        
        self.help.setHtml('The R Executor widget provides direct access to the R session that runs under RedR.  R Executor can recieve any output from an R compatible widget.  The recieved data can be shown using the Recieved button.  The R history can be shown by pressing the RHistory button and the complete parsing of any recieved data is shown in the Metadata section.  More infromation is available on the <a href="http://www.red-r.org/?cat=10">RedR website</a>.')
        
        #GUI
        
        #GUIDialog
        self.box = redRGUI.groupBox(self.GUIDialog, "R Executor")
        self.infob = redRGUI.widgetLabel(self.box, "")
        
        varbutton = redRGUI.button(self.box, "Recieved", callback = self.putrecieved, width = 150)
        history = redRGUI.button(self.box, "RHistory", callback = self.putRHistory, width = 150)
        redRGUI.button(self.box, "Clear Output", callback = self.clearOutput)
        self.infoa = redRGUI.widgetLabel(self.box, "")
        # grid
        area = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        leftArea = redRGUI.widgetBox(area)
        rightArea = redRGUI.widgetBox(area)

        runbox = redRGUI.groupBox(rightArea, label = "Command Line", orientation='horizontal')
        self.command = redRGUI.lineEdit(runbox, "", label = "R Command", orientation=QHBoxLayout())
        processbutton = redRGUI.button(runbox, label = "Run", callback = self.runR, width=100)

        self.dataBox = redRGUI.groupBox(leftArea, label = "Input Infromation")
        self.infov = redRGUI.widgetLabel(self.dataBox, "No Input")
        
        self.metadataBox = redRGUI.widgetBox(leftArea, "Metadata")
        self.infoM = redRGUI.widgetLabel(self.metadataBox, "No Meta Data")
        self.metadataLB = redRGUI.listBox(self.metadataBox, callback = self.insertMetaDataVar)

        self.thistext = redRGUI.textEdit(leftArea)

        #sendbox = redRGUI.groupBox(leftArea, "Send Box")
        #self.sendthis = redRGUI.lineEdit(sendbox,"", label = "Send")
        sendbutton = redRGUI.button(runbox, label = "Send", callback =self.sendThis, width=100)
        self.resize(700,500)
        self.move(300, 25)
        self.autoShowDialog = 0
        
    def clearOutput(self):
        self.thistext.clear()
    def putrecieved(self):
        self.command.setText(str(self.data))
        
    def insertMetaDataVar(self):
        tmp = str(self.olddata[str(self.metadataLB.selectedItems()[0].text())])
        self.infoM.setText(tmp)
        self.command.setText(tmp)
    def sendThis(self):
        
        self.sendt = {'data':str(self.command.text()), 'parent':str(self.command.text())}
        thisdata = self.sendt['data']
        thisdataclass = self.R('class('+thisdata+')')
        if thisdataclass.__class__.__name__ == 'list': #this is a special R type so just send as generic
            self.rSend('R.object', self.sendt)
        elif thisdataclass.__class__.__name__ == 'str':
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                self.rSend('R Vector', self.sendt)
            elif thisdataclass == 'character': #we have a character vector as the object
                self.rSend('R Vector', self.sendt)
            elif thisdataclass == 'data.frame': # the object is a data.frame
                self.R('cm_'+self.sendt['data']+'<-data.frame(row.names = rownames('+self.sendt['data']+'))')
                self.sendt['cm'] = 'cm_'+self.sendt['data']
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
        self.R('txt<-"R error occured" #Benign error in case a real error occurs')
        self.R('txt<-capture.output('+str(self.command.text())+')')

        pasted = self.R('paste(txt, collapse = " \n")')
        # if type(pasted) != type(''):
            # pasted = 'Error occured with evaluation, please chech output for error.'
        self.thistext.insertPlainText('>>>'+str(self.command.text())+'##Done')
        self.thistext.insertHtml('<br><pre>'+pasted+'<\pre><br>')
        self.thistext.setAlignment(Qt.AlignBottom)
    
    def putRHistory(self):
        self.thistext.clear()
        self.thistext.insertHtml(OWRpy.Rhistory)
    def process(self, data):
        for output in self.outputs:
            self.rSend(output[0], None, 0)
        self.data = ''
        if data:
            self.data = str(data['data'])
            self.olddata = data
            for key in self.olddata.keys():
                self.metadataLB.addItem(key)
            self.infob.setText(self.data)
            # logic to handle assignment of the data elements
            thisclass = self.R('class('+self.data+')')
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
        self.infov.setText("Numeric Vector Connected of length %s" % str(self.R('length('+self.data+')')))
    def isCharacter(self):
        self.infov.setText("Character Vector Connected of length %s" % str(self.R('length('+self.data+')')))
    def isDataFrame(self):
        self.infov.setText("Data Frame Connected with %s columns" % str(self.R('length('+self.data+')')))
        colnames = self.R('colnames('+self.data+')')
        if colnames != 'NULL' and self.dfselected == None:
            self.dfselected = redRGUI.listBox(self.dataBox, self)
            for e in colnames:
                self.dfselected.addItem(e)
        elif colnames != 'NULL' and self.dfselected != None:
            self.dfselected.clear()
            for e in colnames:
                self.dfselected.addItem(e)
    def isMatrix(self):
        self.infov.setText("Matrix connected with %s elements and %s columns" % (str(self.R('length('+self.data+')')), str(self.R('length('+self.data+'[1,])'))))
        colnames = self.R('colnames('+self.data+')')
        if colnames != 'NULL' and colnames != '' and colnames != 'None' and colnames != None:
            self.dfselected = redRGUI.listBox(self.dataBox, self)
            try:
                for e in colnames:
                    self.dfselected.addItem(e)
            except:
                print 'Error with colnames, may not exist.'
    def isList(self):
        self.infov.setText("List object connected with %s elements" % str(self.R('length('+self.data+')')))
        
        