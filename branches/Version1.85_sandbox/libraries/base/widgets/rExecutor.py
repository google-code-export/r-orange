"""
<name>R Executor</name>
<tags>Special, R</tags>
<icon>rexecutor.png</icon>
"""

from OWRpy import *
import redRGUI, signals
import redRGUI
import redRi18n
_ = redRi18n.get_(package = 'base')
class rExecutor(OWRpy):
    settingsList = ['command', 'sendthis', 'sendt']
    def __init__(self, **kwargs):
        #OWWidget.__init__(self, parent, signalManager, "Sample Data")
        OWRpy.__init__(self, wantGUIDialog = 1, **kwargs)
        
        self.command = ''
        self.sendthis = ''
        self.sendt = {}
        self.dfselected = None
        self.setRvariableNames(['rExecutor', 'rExecutor_cm'])
        
        
        self.inputs.addInput('id0', _('R.object'), signals.base.RVariable, self.process)

        self.outputs.addOutput('id0', _('R Data Frame'), signals.base.RDataFrame)
        self.outputs.addOutput('id1', _('R List'), signals.base.RList)
        self.outputs.addOutput('id2', _('R Vector'), signals.base.RVector)
        self.outputs.addOutput('id3', _('R.object'), 'All')
        self.outputs.addOutput('id4', _('R Matrix'), signals.base.RMatrix)

        #self.breakme()
        
        #self.help.setHtml('The R Executor widget provides direct access to the R session that runs under RedR.  R Executor can recieve any output from an R compatible widget.  The recieved data can be shown using the Recieved button.  The R history can be shown by pressing the RHistory button and the complete parsing of any recieved data is shown in the Metadata section.  More infromation is available on the <a href="http://www.red-r.org/?cat=10">RedR website</a>.')
        
        #GUI
        
        #GUIDialog
        self.box = redRGUI.base.groupBox(self.GUIDialog, _("R Executor Advanced"))
        self.infob = redRGUI.base.widgetLabel(self.box, "")
        
        self.infoa = redRGUI.base.widgetLabel(self.box, "")
        # grid
        area = redRGUI.base.widgetBox(self.controlArea, orientation = 'horizontal')
        area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        leftArea = redRGUI.base.widgetBox(self.box)
        leftArea.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        rightArea = redRGUI.base.widgetBox(area)

        runbox = redRGUI.base.groupBox(rightArea, label = _("Command Edit:"), orientation='horizontal')
        runbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        #self.command = redRGUI.base.lineEdit(runbox, "", orientation=QHBoxLayout(), callback = self.runR, width = -1)
        self.command = redRGUI.base.textEdit(runbox, label = _('Command Edit:'), displayLabel=False)
        #self.command.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vbox=redRGUI.base.widgetBox(runbox)
        processbutton = redRGUI.base.button(vbox, label = _("&Run"), callback = self.runR, width=100)
        sendbutton = redRGUI.base.button(vbox, label = _("&Send"), toolTip = _('Send the data in the command line into the Red-R schema.'), callback =self.sendThis, width=100)

        statusBox = redRGUI.base.groupBox(rightArea, label = _("Status"))
        self.sendStatus = redRGUI.base.widgetLabel(statusBox, _('Nothing Sent'))
        self.dataBox = redRGUI.base.groupBox(leftArea, label = _("Input Infromation"))
        self.mystatus = redRGUI.base.widgetLabel(self.dataBox, _("No Input"))
        
        # self.metadataBox = redRGUI.base.widgetBox(leftArea, _("Metadata"))
        # self.infoM = redRGUI.base.widgetLabel(self.metadataBox, _("No Meta Data"))
        # self.metadataLB = redRGUI.base.listBox(self.metadataBox, callback = self.insertMetaDataVar)
        varbutton = redRGUI.base.button(leftArea, _("Recieved"), callback = self.putrecieved, width = 150)
        history = redRGUI.base.button(leftArea, _("RHistory"), callback = self.putRHistory, width = 150)
        redRGUI.base.button(leftArea, _("Clear Output"), callback = self.clearOutput)
        
        self.lsList = redRGUI.base.listBox(self.box, label = _('Available R Items'), items = self.R('ls()', wantType = 'list'), callback = self.addlsList)
        redRGUI.base.button(self.box, 'Refresh List', callback = self.refreshLsList)

        self.thistext = redRGUI.base.textEdit(rightArea,label=_('Output'), displayLabel=False)


    def addlsList(self):
        self.command.insertPlainText(unicode(self.lsList.selectedItems().values()[0]))
    def refreshLsList(self):
        self.lsList.update(self.R('ls()', wantType = 'list'))
    def clearOutput(self):
        self.thistext.clear()
    def putrecieved(self):
        self.command.insert(unicode(self.data))
    def sendThis(self):
        if unicode(self.command.textCursor().selectedText()) != '':
                text = unicode(self.command.textCursor().selectedText())
        else:
                self.sendStatus.setText(_('No object Selected'))
                return
        thisdataclass = self.R('class('+unicode(text)+')')
        thisdata = unicode(text)
        # use upclassing to convert to signals class
        if thisdataclass.__class__.__name__ == 'list': #this is a special R type so just send as generic     
            newData = signals.base.RVariable(self, data = unicode(text))
            self.rSend("id3", newData)
        elif thisdataclass.__class__.__name__ == 'str':
            if thisdataclass in ['numeric', 'character', 'logical']: # we have a numeric vector as the object
                newData = signals.base.RVector(self, data = unicode(text))
                self.rSend("id2", newData)
                self.sendStatus.setText(thisdata+_(' sent through the R Vector channel'))
            elif thisdataclass in ['data.frame']:
                newData = signals.base.RDataFrame(self, data = unicode(text))
                self.rSend("id0", newData)
                self.sendStatus.setText(thisdata+_(' sent through the R Data Frame channel'))
            elif thisdataclass in ['matrix']:
                newData = signals.base.RMatrix(self, data = unicode(text))
                self.rSend("id4", newData)
                self.sendStatus.setText(thisdata+_(' sent through the Matrix channel'))
            elif thisdataclass == 'list': # the object is a list
                for i in range(self.R('length('+text+')')):
                    if self.R('class(%s[[%s]])' % (text, i), silent = True) not in ['numeric', 'character', 'real', 'complex', 'factor']:
                        newData = ral.RArbitraryList(self, data = self.sendThis)
                        self.status.setText(_('Data sent through the R Arbitrary List channel'))
                        self.rSend('ral', newData)
                        return
                newData = signals.base.RList(self, data = unicode(text))
                self.rSend("id1", newData)
                self.sendStatus.setText(thisdata+_(' sent through the R List channel'))
            else:    # the data is of a non-normal type send anyway as generic
                newData = signals.base.RVariable(self, data = unicode(text))
                self.rSend("id3", newData)
                self.sendStatus.setText(thisdata+_(' sent through the R Object channel'))
        else:
            newData = signals.base.RVariable(self, data = unicode(text))
            self.rSend("id3", newData)
            self.sendStatus.setText(thisdata+' sent through the R Object channel')
    def runR(self):
        #self.R('txt<-"R error occured" #Benign error in case a real error occurs')
        try:
            if unicode(self.command.textCursor().selectedText()) != '':
                text = unicode(self.command.textCursor().selectedText())
            else:
                text = unicode(self.command.toPlainText())
            output = self.R('capture.output(eval(parse(text = \"'+unicode(text).replace('\"', '\\\"')+'\")))', wantType = 'list', silent = True)
            self.thistext.insertPlainText('\n'+'\n'.join(output)+'\n')
            self.thistext.setAlignment(Qt.AlignBottom)
        except Exception as inst:
            self.thistext.insertPlainText(_('Error Occurred: %s') % inst)
    def putRHistory(self):
        self.thistext.clear()
        self.thistext.insertPlainText('\n'.join(OWRpy.globalRHistory))
    def process(self, data):
        for output in self.outputs.outputIDs():
            self.rSend(output, None, 0)
        self.data = ''
        if data:
            self.data = unicode(data.getData())
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
                    self.mystatus.setText(_("R object is of non-standard type."))
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
                        self.mystatus.setText(_("R object is of non-standard type."))
                    
        else: return
    
    def isNumeric(self):
        self.mystatus.setText(_("Numeric Vector Connected of length %s") % unicode(self.R('length('+self.data+')')))
    def isCharacter(self):
        self.mystatus.setText(_("Character Vector Connected of length %s") % unicode(self.R('length('+self.data+')')))
    def isDataFrame(self):
        self.mystatus.setText(_("Data Frame Connected with %s columns") % unicode(self.R('length('+self.data+')')))
        colnames = self.R('colnames('+self.data+')')
        if colnames != 'NULL' and self.dfselected == None:
            self.dfselected = redRGUI.base.listBox(self.dataBox, self)
            for e in colnames:
                self.dfselected.addItem(e)
        elif colnames != 'NULL' and self.dfselected != None:
            self.dfselected.clear()
            for e in colnames:
                self.dfselected.addItem(e)
    def isMatrix(self):
        self.mystatus.setText(_("Matrix connected with %s elements and %s columns") % (unicode(self.R('length('+self.data+')')), unicode(self.R('length('+self.data+'[1,])'))))
        colnames = self.R('colnames('+self.data+')')
        if colnames != 'NULL' and colnames != '' and colnames != 'None' and colnames != None:
            self.dfselected = redRGUI.base.listBox(self.dataBox, self)
            try:
                for e in colnames:
                    self.dfselected.addItem(e)
            except:
                print _('Error with colnames, may not exist.')
    def isList(self):
        self.mystatus.setText(_("List object connected with %s elements") % unicode(self.R('length('+self.data+')')))
    
        
        