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
import libraries.base.signalClasses.REnvironment as renv
import libraries.base.signalClasses.RVariable as rvar
import libraries.base.signalClasses.RVector as rvec
import libraries.base.signalClasses.RList as rlist
import libraries.base.signalClasses.RMatrix as rmat
import libraries.base.signalClasses.RDataFrame as rdf
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.widgetBox import widgetBox
class RVarSeparator(OWRpy): 
    globalSettingsList = ['sendOnSelect']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
       
        self.inputs = [('R Session', renv.REnvironment, self.process)]
        self.outputs = [('R Session', renv.REnvironment), ('R.object', rvar.RVariable), 
        ('R Data Frame', rdf.RDataFrame), ('R List', rlist.RList), ('R Vector', rvec.RVector)]
       
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
                newData = rvec.RVector(data = self.sendThis)
                self.rSend('R Vector', newData)
                self.status.setText('Data sent through the R Vector channel')
            elif dataClass == 'character': #we have a character vector as the object
                newData = rvec.RVector(data = self.sendThis)
                self.rSend('R Vector', newData)
                self.status.setText('Data sent through the R Vector channel')
            elif dataClass == 'data.frame': # the object is a data.frame
                newData = rdf.RDataFrame(data = self.sendThis)
                self.rSend('R Data Frame', newData)
                self.status.setText('Data sent through the R Data Frame channel')
            elif dataClass == 'matrix': # the object is a matrix
                
                newData = rmat.RMatrix(data = self.sendThis)
                
                self.rSend('R Data Frame', newData)
                self.status.setText('Data sent through the R Data Frame channel')
            elif dataClass == 'list': # the object is a list
                newData = rlist.RList(data = self.sendThis)
                self.rSend('R List', newData)
                self.status.setText('Data sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic  
                newData = rvar.RVariable(data = self.sendThis)
                self.rSend('R.object', newData)
                self.status.setText('Data sent through the R Object channel')
        else:
            newData = rvar.RVariable(data = self.sendThis)
            self.rSend('R.object', newData)
            self.status.setText('Data sent through the R Object channel')
            
    def getReportText(self, fileDir):
        text = 'The variable listed below was sent from this widget.\n\n'
        return text