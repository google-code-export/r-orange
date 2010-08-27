"""
<name>R Variable Selection</name>
<author>Kyle R. Covington</author>
<description>Separates variables from an environment and sends them.  Generally used with the R Loader Widget.</description>
<tags>R</tags>
<icon>rexecutor.png</icon>
<priority>10</priority>
<inputWidgets></inputWidgets>
<outputWidgets>plotting_plot, base_rViewer, base_summary</outputWidgets>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.REnvironment import REnvironment as redRREnvironment
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RList import RList as redRRList
import libraries.base.signalClasses.RMatrix as rmat
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.widgetBox import widgetBox
class RVarSeparator(OWRpy): 
    globalSettingsList = ['sendOnSelect']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
       
        self.inputs.addInput('id0', 'R Environment', redRREnvironment, self.process)

        self.outputs.addOutput('id0', 'R Session', redRREnvironment)
        self.outputs.addOutput('id1', 'Non-Standard R Variable', redRRVariable)
        self.outputs.addOutput('id2', 'R Data Frame (Data Table)', redRRDataFrame)
        self.outputs.addOutput('id3', 'R List', redRRList)
        self.outputs.addOutput('id4', 'R Vector', redRRVector)

       
        # self.help.setHtml('The R Variable Separator is used to separate variables from a loaded R session.  Connecting the R Loader widget to this widget will display a list of available variables in the local environment to which the session was loaded.  Clicking on an element in the list will send that element on to downstream widgets.  One should take note of the class of the element that is sent as this will specify the output connection of the data.  More infromation is available on the <a href="http://www.red-r.org/?cat=10">RedR website</a>.')

        self.controlArea.setMinimumWidth(300)
        self.varBox = listBox(self.controlArea, label = 'Variables', callback = self.select)
        
        box = widgetBox(self.controlArea, orientation='horizontal') 
        #self.filecombo.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.controlArea.layout().setAlignment(box,Qt.AlignRight)
        
        self.sendOnSelect = checkBox(box,buttons=['Send on select'], setChecked = ['Send on select'], 
        toolTips=['Commit variable on select from the list'])
        button(box,label='Commit',callback=self.commit)

        
        
    
    def process(self, data):
        if not data: return
        self.envName = data.getData()

        dataList = self.R('local(ls(), '+self.envName+')', wantType = 'list')
        if type(dataList) == type([]):
            self.varBox.update(dataList)
        elif type(dataList) == type(None):
            self.status.setText('No data in the R session')
            return
    def select(self):
        if 'Send on select' in self.sendOnSelect.getChecked():
            self.commit()
            
    def commit(self):
        #must declare explilcitly as a string or an error will occur.  We remove NA's just in case they are in the data
        self.sendThis = str('local('+self.varBox.selectedItems()[0].text()+', '+self.envName+')') 
        
        #put logic for finding the type of variable that the object is and sending it from that channel of the output
        
        dataClass = self.R('class('+self.sendThis+')')
            
        if type(dataClass) is str:
            if dataClass == 'numeric': # we have a numeric vector as the object
                newData = redRRVector(data = self.sendThis)
                self.rSend('id4', newData)
                self.status.setText('Data sent through the R Vector channel')
            elif dataClass == 'character': #we have a character vector as the object
                newData = redRRVector(data = self.sendThis)
                self.rSend('id4', newData)
                self.status.setText('Data sent through the R Vector channel')
            elif dataClass == 'data.frame': # the object is a data.frame
                newData = redRRDataFrame(data = self.sendThis)
                self.rSend('id2', newData)
                self.status.setText('Data sent through the R Data Frame channel')
            elif dataClass == 'matrix': # the object is a matrix
                
                newData = rmat.RMatrix(data = self.sendThis)
                
                self.rSend('id2', newData)
                self.status.setText('Data sent through the R Data Frame channel')
            elif dataClass == 'list': # the object is a list
                newData = redRRList(data = self.sendThis)
                self.rSend('id3', newData)
                self.status.setText('Data sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic  
                newData = redRRVariable(data = self.sendThis)
                self.rSend('id1', newData)
                self.status.setText('Data sent through the R Object channel')
        else:
            newData = redRRVariable(data = self.sendThis)
            self.rSend('id1', newData)
            self.status.setText('Data sent through the R Object channel')
            
    def getReportText(self, fileDir):
        text = 'The variable listed below was sent from this widget.\n\n'
        return text