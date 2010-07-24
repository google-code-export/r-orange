"""
<name>RedRreadShapePoly</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>maptools:readShapePoly</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
import libraries.maptools.signalClasses.ShapeDataFrame as ShapeDataFrame

class RedRreadShapePoly(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "readShapePoly", wantMainArea = 0, resizingEnabled = 1)
        self.require_librarys(['maptools'])
        self.setRvariableNames(["readShapePoly"])
        self.data = {}
        self.fileName = ''
        self.outputs = [("readShapePoly Output", ShapeDataFrame.ShapeDataFrame)]
        redRGUI.button(self.controlArea, 'Read File', callback = self.browseFile)
        self.RFunctionParamrepair_radioButtons = redRGUI.radioButtons(self.controlArea, label = "repair:", buttons = ["TRUE","FALSE"], setChecked = "FALSE")
        self.RFunctionParamverbose_radioButtons = redRGUI.radioButtons(self.controlArea, label = "verbose:", buttons = ["TRUE","FALSE"], setChecked = "FALSE")
        self.RFunctionParamdelete_null_obj_radioButtons = redRGUI.radioButtons(self.controlArea, label = "delete_null_obj:", buttons = ["TRUE","FALSE"], setChecked = "FALSE")
        self.RFunctionParamforce_ring_radioButtons = redRGUI.radioButtons(self.controlArea, label = "force_ring:", buttons = ["TRUE","FALSE"], setChecked = "FALSE")
        self.RFunctionParamproj4string_lineEdit = redRGUI.lineEdit(self.controlArea, label = "proj4string:", text = '')
        
        self.RFunctionParamIDvar_lineEdit = redRGUI.lineEdit(self.controlArea, label = "IDvar:", text = '')
        self.RFunctionParamretrieve_ABS_null_radioButtons = redRGUI.radioButtons(self.controlArea, label = "retrieve_ABS_null:", buttons = ["TRUE","FALSE"], setChecked = "FALSE")
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def browseFile(self): 
        print self.fileName
        fn = QFileDialog.getOpenFileName(self, "Open File", self.fileName,
        "Shape Poly File (*.shp);; All Files (*.*)")
        if fn.isEmpty(): return
        self.fileName = str(fn)
        
    def commitFunction(self):
        if str(self.fileName) == '': return
        injection = []
        ## make commit function for self.RFunctionParamrepair_radioButtons
        injection.append('repair = '+str(self.RFunctionParamrepair_radioButtons.getChecked()))
        ## make commit function for self.RFunctionParamverbose_radioButtons 
        injection.append('verbose = '+str(self.RFunctionParamverbose_radioButtons.getChecked()))
        ## make commit function for self.RFunctionParamdelete_null_obj_radioButtons
        injection.append('delete_null_obj = '+str(self.RFunctionParamdelete_null_obj_radioButtons.getChecked()))
        ## make commit function for self.RFunctionParamforce_ring_radioButtons
        injection.append('force_ring = '+str(self.RFunctionParamforce_ring_radioButtons.getChecked()))
        if str(self.RFunctionParamproj4string_lineEdit.text()) != '':
            string = 'proj4string='+str(self.RFunctionParamproj4string_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamIDvar_lineEdit.text()) != '':
            string = 'IDvar='+str(self.RFunctionParamIDvar_lineEdit.text())+''
            injection.append(string)
        ## make commit function for self.RFunctionParamretrieve_ABS_null_radioButtons

        inj = ','.join(injection)
        self.R(self.Rvariables['readShapePoly']+'<-readShapePoly(fn = \''+self.fileName.replace('\\','/')+'\','+inj+')')
        newData = ShapeDataFrame.ShapeDataFrame(data = self.Rvariables["readShapePoly"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("readShapePoly Output", newData)
