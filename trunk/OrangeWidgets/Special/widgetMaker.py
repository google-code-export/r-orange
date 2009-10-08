"""
<name>Widget Maker</name>
<description>A widget for making the initial framework of a functional widget given an R package and function.</description>
<icon>icons/widgetMaker.png</icon>
<author>Kyle R. Covington</author>
"""

from OWRpy import *
import OWGUI

class widgetMaker(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        settingsList = ['output_txt', 'parameters']
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 1, resizingEnabled = 1)
        
        self.packageName = ''
        self.functionParams = ''
        self.functionName = ''
        self.widgetInputsName = []
        self.widgetInputsClass = []
        self.widgetInputsFunction = []
        self.numberInputs = 0
        self.numberOutputs = 0
        self.captureROutput = 0
        
        self.fieldList = {}
        self.functionInputs = {}
        self.functionAllowOutput = 1
        self.processOnConnect = 1
        
        self.inputs = None
        self.outputs = None
        
        # GUI
        # several tabs with different parameters such as loading in a function, setting parameters, setting inputs and outputs
        
        box = OWGUI.widgetBox(self.controlArea, "")
        self.infoa = OWGUI.widgetLabel(box, '')
        OWGUI.lineEdit(box, self, 'packageName', label = 'Package:', orientation = 1)
        OWGUI.button(box, self, 'Load Package', callback = self.loadRPackage)
        OWGUI.lineEdit(box, self, 'functionName', label = 'Function Name:', orientation = 1)
        OWGUI.button(box, self, 'Parse Function', callback = self.parseFunction)
        
        box = OWGUI.widgetBox(self.controlArea, "Inputs and Outputs")
        self.inputArea = QTableWidget()
        box.layout().addWidget(self.inputArea)
        self.inputArea.setColumnCount(3)
        
        self.inputArea.hide()
        self.connect(self.inputArea, SIGNAL("itemClicked(QTableWidgetItem*)"), self.inputcellClicked)
        OWGUI.button(box, self, 'Accept Inputs', callback = self.acceptInputs)
        OWGUI.checkBox(box, self, 'functionAllowOutput', 'Allow Output')
        OWGUI.checkBox(box, self, 'captureROutput', 'Show Output')
        
        OWGUI.button(box, self, 'Generate Code', callback = self.generateCode)
        OWGUI.button(box, self, 'Launch Widget', callback = self.launch)
        
        self.splitCanvas = QSplitter(Qt.Vertical, self.mainArea)
        self.mainArea.layout().addWidget(self.splitCanvas)
        
        codebox = OWGUI.widgetBox(self, "Code Box")
        self.splitCanvas.addWidget(codebox)

        self.codeArea = QTextEdit()
        codebox.layout().addWidget(self.codeArea)
        

    def launch(self):
        import orngEnviron, orngRegistry, orngCanvas
        widgetDirName = os.path.realpath(orngEnviron.directoryNames["widgetDir"])
        #print 'dir:' + widgetDirName
        path = widgetDirName +  "/Prototypes/" + self.functionName.replace('.', '_') + ".py"
        #print 'path:' + path
        file = open(path, "wt")
        tmpCode = self.completeCode
        tmpCode = tmpCode.replace('<pre>', '')
        tmpCode = tmpCode.replace('</pre>', '')
        tmpCode = tmpCode.replace('&lt;', '<')
        tmpCode = tmpCode.replace('&gt;', '>')
        file.write(tmpCode)
        file.close()
        
        #reload all the widgets including those in the prototype dir we just created 
        #orngCanvas.OrangeCanvasDlg.reloadWidgets()
        
        #orngRegistry.readCategories()
        qApp.canvasDlg.reloadWidgets()  # yay!!! it works
        
        # need to work out how to update the widget icons in the tabs to show the new widget
        #or create a new button that will launch the new widget
        # self.createWidgetsToolbar()
        
        
        
    def loadRPackage(self):
        
        self.require_librarys([self.packageName])
        
    def parseFunction(self):
        self.args = {}
        try:
            holder = self.R('capture.output(args('+self.functionName+'))')
            s = ''
            functionParams = s.join(holder)
            print self.functionName
            self.infoa.setText("Function called successfully.")
            print 'function called successfully'
            print str(self.functionParams)
        except:
            self.infoa.setText("Error with calling function.")
            return
            
        start = functionParams.find('(')+1 #where the args start 
        print str(start)
        end = functionParams.rfind(')') # where the args end.
        print 'end'+str(end)
        tmp = functionParams[start:end]
        
        tmp = tmp.replace(' ','') #remove the spaces
        tmp = tmp.replace("','", '##')
        tmp = tmp.replace('","', '##')
        tmp = tmp.split(',')
        for el in tmp:
            tmp2 = el.split('=')
            tmp2[0] = tmp2[0].replace('.', '_')
            if tmp2[0] != '___': # don't pay attention to optional params
                if len(tmp2) > 1:
                    
                    self.args[tmp2[0]] = tmp2[1]
                else:
                    self.args[tmp2[0]] = ''
            
        for arg in self.args.keys():
            if self.args[arg][0:2] == 'c(':
                self.args[arg] = self.args[arg].replace("'", '')
                self.args[arg] = self.args[arg].replace('"', '')
                start = self.args[arg].find('(')+1
                end = self.args[arg].rfind(')')
                self.args[arg] = self.args[arg][start:end] #strip out the brackets
                self.args[arg] = self.args[arg].replace('##', ",")
                self.args[arg] = self.args[arg].split(',')
                
        self.updateInputs()
        
    def updateInputs(self):
        self.inputArea.clear()
        self.inputArea.setRowCount(int(len(self.args.keys())))

        self.inputArea.show()
        self.inputArea.setHorizontalHeaderLabels(['Name', 'Class', 'Function'])
        n=0
        for arg in self.args.keys():
            arg = arg.replace('.', '_') # python uses points for class refference
            itemname = QTableWidgetItem(str(arg))
            #itemClass = QTableWidgetItem
            self.inputArea.setItem(n,0,itemname)
            cw = QComboBox()
            cw.addItems(['Widget Input', 'Connection Input'])
            self.inputArea.setCellWidget(n,1,cw)
            n += 1
        
    def acceptInputs(self): #accept the criteria in the input Area
        for i in xrange(self.inputArea.rowCount()):
            print 'i:'+str(i)
            combo = self.inputArea.cellWidget(i, 1)
            print combo
            if combo.currentText() == 'Widget Input':
                print str(self.inputArea.item(i ,0).text())
                self.fieldList[str(self.inputArea.item(i, 0).text())] = ''
            else:
                self.functionInputs[str(self.inputArea.item(i,0).text())] = ''
        print self.fieldList
        print self.functionInputs
        for item in self.fieldList.keys():
            item = item.replace('.', '_')
            self.fieldList[item] = self.args[item]
            
    def inputcellClicked(self, item):
        self.inputArea.editItem(item)
    
    def generateCode(self):
        self.makeHeader()
        self.makeInitHeader()
        self.makeGUI()
        self.makeProcessSignals()
        self.makeCommitFunction()
        #self.makeRsendFunction()
        
        self.combineCode()
        
    def makeHeader(self):
        self.headerCode = '"""\n'
        self.headerCode += '&lt;name&gt;'+self.functionName+'&lt;/name&gt;\n'
        self.headerCode += '&lt;author&gt;Generated using Widget Maker written by Kyle R. Covington&lt;/author&gt;\n'
        self.headerCode += '"""\n'
        self.headerCode += 'from OWRpy import * \n'
        self.headerCode += 'import OWGUI \n'
        self.headerCode += 'import RRGUI \n'
        
    def makeInitHeader(self):
        self.initCode = ''
        self.initCode += 'class '+self.functionName.replace('.', '_')+'(OWRpy): \n'
        self.initCode += '\tsettingsList = []\n'
        self.initCode += '\tdef __init__(self, parent=None, signalManager=None):\n'

        self.initCode += '\t\tOWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)\n'
        if self.functionAllowOutput:
            self.initCode += '\t\tself.setRvariableNames(["'+self.functionName+'"])\n'
        for element in self.fieldList.keys():
            if element == '___':
                pass
            else:
                if self.fieldList[element] == '' or self.fieldList[element] == "":
                    self.initCode += '\t\tself.RFunctionParam_'+element+' = ""\n'
                elif type(self.fieldList[element]) == type([]): #the fieldList is a list
                    self.initCode += '\t\tself.RFunctionParam_'+element+' = 0\n' #set the item to the first one
                else:
                    self.fieldList[element] = self.fieldList[element].replace('"', '')
                    self.fieldList[element] = self.fieldList[element].replace("'", "")
                    self.initCode += '\t\tself.RFunctionParam_'+element+' = "'+str(self.fieldList[element])+'"\n'
        self.initCode += '\t\tself.loadSettings() \n'
        if len(self.functionInputs.keys()) > 0:
            for inputName in self.functionInputs.keys():
                self.initCode += "\t\tself.RFunctionParam_"+inputName+" = ''\n"
            self.initCode += '\t\tself.inputs = ['
            for element in self.functionInputs.keys():
                self.initCode += '("'+element+'", RvarClasses.RVariable, self.process'+element+'),'
            self.initCode = self.initCode[:len(self.initCode)-1]
            self.initCode += ']\n'
        if self.functionAllowOutput:
            self.initCode += '\t\tself.outputs = [("'+self.functionName+' Output", RvarClasses.RVariable)]\n'
        self.initCode += '\t\t\n'
        
    def makeGUI(self):
        self.guiCode = ''
        self.guiCode += '\t\tbox = OWGUI.widgetBox(self.controlArea, "Widget Box")\n'
        for element in self.fieldList.keys():
            if element == '___':
                pass
            else:
                if type(self.fieldList[element]) == type(''):
                    self.guiCode += '\t\tself.RFUnctionParam'+ element +'_lineEdit =  RRGUI.lineEdit(box, "RFUnctionParam'+ element + '_lineEdit", self, "RFunctionParam_'+element+'", label = "'+element+':")\n'
                elif type(self.fieldList[element]) == type([]):
                    self.guiCode += '\t\tself.RFunctionParam' + element +'_comboBox = RRGUI.comboBox(box, "RFunctionParam'+ element + '_comboBox", self, "RFunctionParam_'+element+'", label = "'+element+':", items = '+str(self.fieldList[element])+')\n'
        self.guiCode += '\t\tOWGUI.button(box, self, "Commit", callback = self.commitFunction)\n'
        if self.captureROutput:
            self.guiCode += '\t\tself.RoutputWindow = RRGUI.textEdit("RoutputWindow", self)\n'
            self.guiCode += '\t\tbox.layout().addWidget(self.RoutputWindow)\n'

    def makeProcessSignals(self):
        self.processSignals = ''
        for inputName in self.functionInputs.keys():
            self.processSignals += '\tdef process'+inputName+'(self, data):\n'
            if self.packageName != '':
                self.processSignals += '\t\tself.require_librarys(["'+self.packageName+'"]) \n'
            self.processSignals += '\t\tif data:\n'
            self.processSignals += '\t\t\tself.RFunctionParam_'+inputName+'=data["data"]\n'
            if self.processOnConnect:
                self.processSignals += '\t\t\tself.commitFunction()\n'
                
    def makeCommitFunction(self):
        self.commitFunction = ''
        self.commitFunction += '\tdef commitFunction(self):\n'
        for inputName in self.functionInputs.keys():
            self.commitFunction += "\t\tif self.RFunctionParam_"+inputName+" == '': return\n"
        self.commitFunction += "\t\tself.R("
        if self.captureROutput:
            self.commitFunction += "'txt&lt;-capture.output('+"
        if self.functionAllowOutput:
            self.commitFunction += "self.Rvariables['"+self.functionName+"']+'&lt;-"+self.functionName+"("
        else:
            self.commitFunction += "'"+self.functionName+"("
        for element in self.functionInputs.keys():
            if element != '___':
                element = element.replace('_', '.')
                self.commitFunction += element+"='+str(self.RFunctionParam_"+element+")+',"
        #self.commitFunction = self.commitFunction[:-2] #remove the last element
        for element in self.fieldList.keys():
            if element == '...':
                pass
            else:
                self.commitFunction += element+"='+str(self.RFunctionParam_"+element+")+',"
        self.commitFunction = self.commitFunction[:-1]
        if self.captureROutput:
            self.commitFunction += ')'
        self.commitFunction += ")')\n"
        if self.captureROutput:
            self.commitFunction += "\t\tself.RoutputWindow.clear()\n"
            self.commitFunction += "\t\ttmp = self.R('paste(txt, collapse =\x22\x5cn\x22)')\n"
            self.commitFunction += "\t\tself.RoutputWindow.insertHtml('&lt;br&gt;&lt;pre&gt;'+tmp+'&lt;/pre&gt;')\n"
            
                    # pasted = self.rsession('paste(txt, collapse = " \n")')
        # self.thistext.insertPlainText('>>>'+self.command+'##Done')
        # self.thistext.insertHtml('<br><pre>'+pasted+'<\pre><br>')
        
        
        if self.functionAllowOutput:
            self.commitFunction += '\t\tself.rSend("'+self.functionName+' Output", {"data":self.Rvariables["'+self.functionName+'"]})\n'
    
    def combineCode(self):
        self.completeCode = '<pre>'
        self.completeCode += self.headerCode+self.initCode+self.guiCode+self.processSignals+self.commitFunction
        self.completeCode += '</pre>'
        self.codeArea.setHtml(self.completeCode)