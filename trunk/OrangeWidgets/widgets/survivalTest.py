"""
<name>Survival Test</name>
<description>Compare one or more sets of survival data.</description>
<icon>icons/survival.png</icon>
<priority>10</priority>
"""
# allows the user to calculate survival or hazard ratios for many kinds of data.  Assumes non-proportional hazards which can be adjusted on an 'advanced' tab if the user wishes.

from OWRpy import *
import OWGUI

    class survivalTest(OWRpy):
    #This widget has no settings list
    def __init__(self, parent=None, signalManager=None):
        settingsList = ['output_txt', 'parameters']
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.output_txt = '' # the R output for the survival test
        self.parameters = [] # start with a blank list
        
        
        self.inputs = [("Data Table", RvarClasses.RDataFrame, self.processData)]
        self.outputs = [("Survival Fit", RvarClasses.RVariable)]
        
        # Start the GUI
        box = OWGUI.widgetBox(self.controlArea, "Options")
        self.eventsList = OWGUI.comboBox(box, self, 'events', label = 'Events')
        self.timeList = OWGUI.comboBox(box, self, 'time', lable = 'Time')
        self.paramsList = OWGUI.listBox(box, self, 'parameters', label = "Parameters")
        
        
        
        output = OWGUI.widgetBox(self.controlArea, "Output")
        self.ROutputViewer = QTextEdit()
        output.layout().addWidget(self.ROutputViewer)
        # End the GUI
        
    def onLoadSavedSession(self):
        self.ROutputViewer.setHtml(self.output_txt)
    
    def processData(self, data):
        self.clear()
        if data != None: #must account for an empty dataset
            self.data = data['data']
            parameters = self.R('colnames('+self.data+')')
            if self.parameters != parameters:
                self.parameters = parameters # resets the GUI if new colnames are detected otherwise skip
                self.refresh()
            else:
                self.commit()
        else:   
            self.ROutputViewer.setHtml("No data connected or sent.  Please check connection")
    def commit(self):
        # stuff for processing the data
    def clear(self):
        self.ROutputViewer.clear()
        
    def refresh(self):
        self.eventsList.clear()
        self.timeList.clear()
        self.paramsList.clear()
        self.eventsList.addItems(self.parameters)
        self.timeList.addItems(self.parameters)