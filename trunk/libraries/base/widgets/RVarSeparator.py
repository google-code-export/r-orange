"""
<name>R Variable Selection</name>
<author>Kyle R. Covington</author>
<description>Separates variables from an environment and sends them.  Generally used with the R Loader Widget.</description>
<tags>R</tags>
<icon>icons/rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
class RVarSeparator(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self,parent, signalManager, "RVarSeparator", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(['separator_cm'])
        
        self.inputs = [('R Session', signals.REnvironment, self.process)]
        self.outputs = [('R Session', signals.REnvironment), ('R.object', signals.RVariable), ('R Data Frame', signals.RDataFrame), ('R List', signals.RList), ('R Vector', signals.RVector)]
        self.setRvariableNames(['sessionEnviron'])
        self.envName = ''
        self.sendthis = {}
        
        
        self.help.setHtml('The R Variable Separator is used to separate variables from a loaded R session.  Connecting the R Loader widget to this widget will display a list of available variables in the local environment to which the session was loaded.  Clicking on an element in the list will send that element on to downstream widgets.  One should take note of the class of the element that is sent as this will specify the output connection of the data.  More infromation is available on the <a href="http://www.red-r.org/?cat=10">RedR website</a>.')
        self.varBox = redRGUI.listBox(self.controlArea, label = 'Variables', callback = self.separate)
        self.sendStatus = redRGUI.widgetLabel(self.controlArea, '')
        #self.status = redRGUI.widgetLabel(self.controlArea, 'status', 'No data to parse')
    
    def process(self, data):
        self.envName = ''
        self.sendthis = {}
        self.sendStatus.setText('')
        if data:
            dataList = self.R('local(ls(), '+data['data']+')', wantType = 'list')
            if type(dataList) == type([]):
                self.varBox.update(dataList)
            elif type(dataList) == type(None):
                self.status.setText('No data in the R session')
                return
            self.envName = data['data']
            self.status.setText('Data Loaded')
        else: 
            self.status.setText('No data to parse')
    def separate(self):
        self.sendthis = {'data':str('local('+self.varBox.selectedItems()[0].text()+', '+self.envName+')')} #must declare explilcitly as a string or an error will occur.  We remove NA's just in case they are in the data
        
        #put logic for finding the type of variable that the object is and sending it from that channel of the output
        
        thisdataclass = self.R('class('+self.sendthis['data']+')')
        if type(thisdataclass) == type([]): #this is a special R type so just send as generic
            self.rSend('R.object', self.sendthis)
            self.status.setText('Ambiguous class Sent')
            
        elif type(thisdataclass) == type(''):
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                newData = signals.RVector(data = self.sendthis['data'])
                self.rSend('R Vector', newData)
                self.status.setText('Numeric vector sent')
                self.sendStatus.setText('Data sent through the R Vector channel')
            elif thisdataclass == 'character': #we have a character vector as the object
                newData = signals.RVector(data = self.sendthis['data'])
                self.rSend('R Vector', newData)
                self.status.setText('Character vector sent')
                self.sendStatus.setText('Data sent through the R Vector channel')
            elif thisdataclass == 'data.frame': # the object is a data.frame

                newData = signals.RDataFrame(data = self.sendthis['data'])
                self.rSend('R Data Frame', newData)
                self.status.setText('Data frame sent')
                self.sendStatus.setText('Data sent through the R Data Frame channel')
            elif thisdataclass == 'matrix': # the object is a matrix
                
                newData = signals.RMatrix(data = self.sendthis['data'])
                
                self.rSend('R Data Frame', newData)
                self.status.setText('Matrix sent')
                self.sendStatus.setText('Data sent through the R Data Frame channel')
            elif thisdataclass == 'list': # the object is a list
                newData = signals.RList(data = self.sendthis['data'])
                self.rSend('R List', newData)
                self.status.setText('List sent')
                self.sendStatus.setText('Data sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic  
                newData = signals.RVariable(data = self.sendthis['data'])
                self.rSend('R.object', newData)
                self.status.setText('Ambiguous class sent')
                self.sendStatus.setText('Data sent through the R Object channel')
            
        else:
            newData = signals.RVariable(data = self.sendthis['data'])
            self.rSend('R.object', newData)
            self.status.setText('Ambiguous class sent')
            self.sendStatus.setText('Data sent through the R Object channel')