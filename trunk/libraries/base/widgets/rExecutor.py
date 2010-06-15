"""
<name>R Executor</name>
<description>Accepts and sends R objects as well as performing R commands</description>
<tags>Special, R</tags>
<icon>rexecutor.png</icon>
<priority>80</priority>
"""

from OWRpy import *
import redRGUI
import libraries.base.signalClasses.RVariable as rvar
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RMatrix as rmat
import libraries.base.signalClasses.RList as rlist
import libraries.base.signalClasses.RVector as rvec
class rExecutor(OWRpy):
    settingsList = ['command', 'sendthis', 'sendt']
    def __init__(self, parent=None, signalManager=None):
        #OWWidget.__init__(self, parent, signalManager, "Sample Data")
        OWRpy.__init__(self, parent, signalManager, 'RExecutor', wantGUIDialog = 1, wandMainArea = 0)
        
        self.command = ''
        self.sendthis = ''
        self.sendt = {}
        self.dfselected = None
        self.setRvariableNames(['rExecutor', 'rExecutor_cm'])
        
        
        self.inputs = [('R.object', rvar.RVariable, self.process)]
        self.outputs = [('R Data Frame', rdf.RDataFrame), ('R List', rlist.RList), ('R Vector', rvec.RVector), ('R.object', 'All'), ('R Matrix', rmat.RMatrix)]
        #self.breakme()
        
        self.help.setHtml('The R Executor widget provides direct access to the R session that runs under RedR.  R Executor can recieve any output from an R compatible widget.  The recieved data can be shown using the Recieved button.  The R history can be shown by pressing the RHistory button and the complete parsing of any recieved data is shown in the Metadata section.  More infromation is available on the <a href="http://www.red-r.org/?cat=10">RedR website</a>.')
        
        #GUI
        
        #GUIDialog
        self.box = redRGUI.groupBox(self.GUIDialog, "R Executor")
        self.infob = redRGUI.widgetLabel(self.box, "")
        
        self.infoa = redRGUI.widgetLabel(self.box, "")
        # grid
        area = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        leftArea = redRGUI.widgetBox(self.box)
        leftArea.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        rightArea = redRGUI.widgetBox(area)

        runbox = redRGUI.groupBox(rightArea, label = "Command Line", orientation='horizontal')
        runbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.command = redRGUI.lineEdit(runbox, "", label = "R Command", orientation=QHBoxLayout(), callback = self.runR, width = -1)
        self.command.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        processbutton = redRGUI.button(runbox, label = "&Run", callback = self.runR, width=100)
        statusBox = redRGUI.groupBox(rightArea, label = "Status")
        self.sendStatus = redRGUI.widgetLabel(statusBox, 'Nothing Sent')
        self.dataBox = redRGUI.groupBox(leftArea, label = "Input Infromation")
        self.status = redRGUI.widgetLabel(self.dataBox, "No Input")
        
        # self.metadataBox = redRGUI.widgetBox(leftArea, "Metadata")
        # self.infoM = redRGUI.widgetLabel(self.metadataBox, "No Meta Data")
        # self.metadataLB = redRGUI.listBox(self.metadataBox, callback = self.insertMetaDataVar)
        varbutton = redRGUI.button(leftArea, "Recieved", callback = self.putrecieved, width = 150)
        history = redRGUI.button(leftArea, "RHistory", callback = self.putRHistory, width = 150)
        redRGUI.button(leftArea, "Clear Output", callback = self.clearOutput)

        self.thistext = redRGUI.textEdit(rightArea)

        sendbutton = redRGUI.button(runbox, label = "&Send", toolTip = 'Send the data in the command line into the Red-R schema.', callback =self.sendThis, width=100)

        
    def clearOutput(self):
        self.thistext.clear()
    def putrecieved(self):
        self.command.setText(str(self.data))
        
    # def insertMetaDataVar(self):
        # tmp = str(self.olddata[str(self.metadataLB.selectedItems()[0].text())])
        # self.thistext.insertHtml(tmp)
        # self.infoM.setText(tmp)
        # self.command.setText(tmp)
    def sendThis(self):
        
        thisdataclass = self.R('class('+str(self.command.text())+')')
        thisdata = str(self.command.text())
        # use upclassing to convert to signals class
        if thisdataclass.__class__.__name__ == 'list': #this is a special R type so just send as generic     
            newData = rvar.RVariable(data = str(self.command.text()))
            self.rSend('R.object', newData)
        elif thisdataclass.__class__.__name__ == 'str':
            if thisdataclass in ['numeric', 'character', 'logical']: # we have a numeric vector as the object
                self.R(self.Rvariables['rExecutor_cm']+'<-list()')
                newData = rvec.RVector(data = str(self.command.text()), cm = self.Rvariables['rExecutor_cm'])
                self.rSend('R Vector', newData)
                self.sendStatus.setText(thisdata+' sent through the R Vector channel')
            elif thisdataclass in ['data.frame']:
                newData = rdf.RDataFrame(data = str(self.command.text()))
                self.rSend('R Data Frame', newData)
                self.sendStatus.setText(thisdata+' sent through the R Data Frame channel')
            elif thisdataclass in ['matrix']:
                newData = rmat.RMatrix(data = str(self.command.text()))
                self.rSend('R Matrix', newData)
                self.sendStatus.setText(thisdata+' sent through the Matrix channel')
            elif thisdataclass == 'list': # the object is a list
                newData = rlist.RList(data = str(self.command.text()))
                self.rSend('R List', newData)
                self.sendStatus.setText(thisdata+' sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic
                newData = rvar.RVariable(data = str(self.command.text()))
                self.rSend('R.object', newData)
                self.sendStatus.setText(thisdata+' sent through the R Object channel')
        else:
            newData = rvar.RVariable(data = str(self.command.text()))
            self.rSend('R.object', newData)
            self.sendStatus.setText(thisdata+' sent through the R Object channel')
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
            self.data = str(data.getData())
            self.olddata = data
            
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
                    self.status.setText("R object is of non-standard type.")
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
                        self.status.setText("R object is of non-standard type.")
                    
        else: return
    
    def isNumeric(self):
        self.status.setText("Numeric Vector Connected of length %s" % str(self.R('length('+self.data+')')))
    def isCharacter(self):
        self.status.setText("Character Vector Connected of length %s" % str(self.R('length('+self.data+')')))
    def isDataFrame(self):
        self.status.setText("Data Frame Connected with %s columns" % str(self.R('length('+self.data+')')))
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
        self.status.setText("Matrix connected with %s elements and %s columns" % (str(self.R('length('+self.data+')')), str(self.R('length('+self.data+'[1,])'))))
        colnames = self.R('colnames('+self.data+')')
        if colnames != 'NULL' and colnames != '' and colnames != 'None' and colnames != None:
            self.dfselected = redRGUI.listBox(self.dataBox, self)
            try:
                for e in colnames:
                    self.dfselected.addItem(e)
            except:
                print 'Error with colnames, may not exist.'
    def isList(self):
        self.status.setText("List object connected with %s elements" % str(self.R('length('+self.data+')')))
        
        