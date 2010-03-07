"""
<name>Get Symbol</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Still a bit of an experimental widget, this widget gets symbol data and brings it into RedR.  Data can be plotted using the barChart widget.</description>
<tags>Finance</tags>
<icon>icons/Finance.PNG</icon>
"""
from OWRpy import * 
import OWGUI 
class getSymbols(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["getSymbols"])
		self.RFunctionParam_src = "yahoo"
		self.RFunctionParam_verbose = "FALSE"
		self.RFunctionParam_warnings = "TRUE"
		self.RFunctionParam_reload_Symbols = "FALSE"
		self.RFunctionParam_Symbols = "NULL"
		self.RFunctionParam_symbol_lookup = "TRUE"
		self.RFunctionParam_env = ".GlobalEnv"
		self.RFunctionParam_auto_assign = "TRUE"
		self.outputs = [("getSymbols Output", RvarClasses.RVariable)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.lineEdit(box, self, "RFunctionParam_Symbols", label = "Symbols:")
		OWGUI.lineEdit(box, self, "RFunctionParam_src", label = "src:")
		OWGUI.lineEdit(box, self, "RFunctionParam_verbose", label = "verbose:")
		OWGUI.lineEdit(box, self, "RFunctionParam_warnings", label = "warnings:")
		OWGUI.lineEdit(box, self, "RFunctionParam_reload_Symbols", label = "reload_Symbols:")

		OWGUI.lineEdit(box, self, "RFunctionParam_symbol_lookup", label = "symbol_lookup:")
		OWGUI.lineEdit(box, self, "RFunctionParam_env", label = "env:")
		OWGUI.lineEdit(box, self, "RFunctionParam_auto_assign", label = "auto_assign:")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def commitFunction(self):
		symbol = self.R(self.Rvariables['getSymbols']+'<-getSymbols(src="'+str(self.RFunctionParam_src)+'",verbose='+str(self.RFunctionParam_verbose)+',warnings='+str(self.RFunctionParam_warnings)+',reload_Symbols='+str(self.RFunctionParam_reload_Symbols)+',Symbols="'+str(self.RFunctionParam_Symbols)+'",symbol_lookup='+str(self.RFunctionParam_symbol_lookup)+',env='+str(self.RFunctionParam_env)+',auto_assign='+str(self.RFunctionParam_auto_assign)+')')
		self.rSend("getSymbols Output", {"data":symbol, "object":self.Rvariables["getSymbols"]})
