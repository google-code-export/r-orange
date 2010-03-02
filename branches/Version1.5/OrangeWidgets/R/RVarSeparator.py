"""
<name>R Variable Separator</name>
<author>Kyle R. Covington</author>
<description>Separates variables from an environment and sends them.  Generally used with the R Loader Widget.</description>
<tags>R</tags>
<icon>icons/rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class RVarSeparator(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self,parent, signalManager, "RVarSeparator", wantMainArea = 0, resizingEnabled = 1)
        self.inputs = [('R Session', RvarClasses.RSession, self.process)]
        self.outputs = [('R Session', RvarClasses.RSession), ('R.object', RvarClasses.RVariable), ('R Data Frame', RvarClasses.RDataFrame), ('R List', RvarClasses.RList), ('R Vector', RvarClasses.RVector)]
        self.setRvariableNames(['sessionEnviron'])
        self.envName = ''
        self.sendthis = {}
        
        
        self.help.setHtml('The R Variable Separator is used to separate variables from a loaded R session.  Connecting the R Loader widget to this widget will display a list of available variables in the local environment to which the session was loaded.  Clicking on an element in the list will send that element on to downstream widgets.  One should take note of the class of the element that is sent as this will specify the output connection of the data.  More infromation is available on the <a href="http://www.red-r.org/?cat=10">RedR website</a>.')
        self.varBox = RRGUI.listBox(self.controlArea, 'varBox', self, callback = self.separate)
        self.statusText = RRGUI.widgetLabel(self.controlArea, 'statusText', self, 'No data to parse')
    
    def process(self, data):
        self.varBox.clear()
        self.envName = ''
        self.sendthis = {}
        if data and 'data' in data:
            dataList = self.R('local(ls(), '+data['data']+')')
            if type(dataList) == type([]):
                self.varBox.addItems(dataList)
            elif type(dataList) == type(''):
                self.varBox.addItem(dataList)
            elif type(dataList) == type(None):
                self.statusText.setText('No data in the R session')
                return
            self.envName = data['data']
            self.statusText.setText('Data Loaded')
        else: 
            self.statusText.setText('No data to parse')
    def separate(self):
        self.sendthis = {'data':str('local('+self.varBox.selectedItems()[0].text()+', '+self.envName+')')} #must declare explilcitly as a string or an error will occur.
        
        #put logic for finding the type of variable that the object is and sending it from that channel of the output
        
        thisdataclass = self.rsession('class('+self.sendthis['data']+')')
        if type(thisdataclass) == type([]): #this is a special R type so just send as generic
            self.rSend('R.object', self.sendthis)
            self.statusText.setText('Ambiguous class Sent')
            
        elif type(thisdataclass) == type(''):
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                self.rSend('R Vector', self.sendthis)
                self.statusText.setText('Numeric vector sent')
            elif thisdataclass == 'character': #we have a character vector as the object
                self.rSend('R Vector', self.sendthis)
                self.statusText.setText('Character vector sent')
            elif thisdataclass == 'data.frame': # the object is a data.frame
                self.rSend('R Data Frame', self.sendthis)
                self.statusText.setText('Data frame sent')
            elif thisdataclass == 'matrix': # the object is a matrix
                self.rSend('R Data Frame', self.sendthis)
                self.statusText.setText('Matrix sent')
            elif thisdataclass == 'list': # the object is a list
                self.rSend('R List', self.sendthis)
                self.statusText.setText('List sent')
            else:    # the data is of a non-normal type send anyway as generic
                self.rSend('R.object', self.sendthis)
                self.statusText.setText('Ambiguous class sent')
            
        else:
            self.rSend('R.object', self.sendthis)
            self.statusText.setText('Ambiguous class sent')
            