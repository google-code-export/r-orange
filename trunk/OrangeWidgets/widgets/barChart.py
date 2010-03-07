"""
<name>barChart</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Still a bit of an experimental widget, this widget plots data from the Get Symbol widget.</description>
<tags>Finance</tags>
<icon>icons/Finance.PNG</icon>
"""
from OWRpy import * 
import OWGUI 
class barChart(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.RFunctionParam_subset = "NULL"
		self.RFunctionParam_time_scale = "NULL"
		self.RFunctionParam_name = "deparse(substitute(x))"
		self.RFunctionParam_show_grid = "TRUE"
		self.RFunctionParam_bar_type = "ohlc"
		self.RFunctionParam_multi_col = "FALSE"
		self.RFunctionParam_theme = ""
		self.RFunctionParam_major_ticks = "auto"
		self.RFunctionParam_minor_ticks = "TRUE"
		self.RFunctionParam_color_vol = "TRUE"
		self.RFunctionParam_type = "bars"
		self.RFunctionParam_TA = ""
		self.RFunctionParam_x = ''
		self.inputs = [("x", RvarClasses.RVariable, self.processx)]
		
		box = OWGUI.widgetBox(self.controlArea, "Widget Box")
		OWGUI.lineEdit(box, self, "RFunctionParam_subset", label = "subset:")
		OWGUI.lineEdit(box, self, "RFunctionParam_time_scale", label = "time_scale:")
		OWGUI.lineEdit(box, self, "RFunctionParam_name", label = "name:")
		OWGUI.lineEdit(box, self, "RFunctionParam_show_grid", label = "show_grid:")
		OWGUI.lineEdit(box, self, "RFunctionParam_bar_type", label = "bar_type:")
		OWGUI.lineEdit(box, self, "RFunctionParam_multi_col", label = "multi_col:")
		OWGUI.lineEdit(box, self, "RFunctionParam_theme", label = "theme:")
		OWGUI.lineEdit(box, self, "RFunctionParam_major_ticks", label = "major_ticks:")
		OWGUI.lineEdit(box, self, "RFunctionParam_minor_ticks", label = "minor_ticks:")
		OWGUI.lineEdit(box, self, "RFunctionParam_color_vol", label = "color_vol:")
		OWGUI.lineEdit(box, self, "RFunctionParam_type", label = "type:")
		OWGUI.lineEdit(box, self, "RFunctionParam_TA", label = "TA:")
		OWGUI.button(box, self, "Commit", callback = self.commitFunction)
	def processx(self, data):
		if data:
			self.RFunctionParam_x=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if self.RFunctionParam_x == '': return
		self.R('barChart(x='+str(self.RFunctionParam_x)+',subset='+str(self.RFunctionParam_subset)+',time_scale='+str(self.RFunctionParam_time_scale)+',name='+str(self.RFunctionParam_name)+',show_grid='+str(self.RFunctionParam_show_grid)+',bar_type="'+str(self.RFunctionParam_bar_type)+'",multi_col='+str(self.RFunctionParam_multi_col)+',theme='+str(self.RFunctionParam_theme)+',major_ticks="'+str(self.RFunctionParam_major_ticks)+'",minor_ticks='+str(self.RFunctionParam_minor_ticks)+',color_vol='+str(self.RFunctionParam_color_vol)+',type="'+str(self.RFunctionParam_type)+'",TA='+str(self.RFunctionParam_TA)+')')
