"""
<name>pamr.train</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
"""
from OWRpy import * 
import OWGUI 
import redRGUI 
class pamr_train(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
		self.setRvariableNames(["pamr.train"])
		self.RFunctionParam_ngroup_survival = "2"
		self.RFunctionParam_n_threshold = "30"
		self.RFunctionParam_offset_percent = "50"
		self.RFunctionParam_hetero = "NULL"
		self.RFunctionParam_remove_zeros = "TRUE"
		self.RFunctionParam_sample_subset = "NULL"
		self.RFunctionParam_se_scale = "NULL"
		self.RFunctionParam_scale_sd = "TRUE"
		self.RFunctionParam_prior = "NULL"
		self.RFunctionParam_threshold_scale = "NULL"
		self.RFunctionParam_threshold = "NULL"
		self.RFunctionParam_sign_contrast = "both"
		self.loadSettings() 
		self.RFunctionParam_data = ''
		self.RFunctionParam_gene_subset = ''
		self.inputs = [("data", RvarClasses.RVariable, self.processdata),("gene_subset", RvarClasses.RVariable, self.processgene_subset)]
		self.outputs = [("pamr.train Output", RvarClasses.RVariable)]
		
		self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = redRGUI.tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamngroup_survival_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "ngroup_survival:")
		self.RFunctionParamn_threshold_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "n_threshold:")
		self.RFunctionParamoffset_percent_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "offset_percent:")
		self.RFunctionParamhetero_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "hetero:")
		self.RFunctionParamremove_zeros_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "remove_zeros:")
		self.RFunctionParamsample_subset_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "sample_subset:")
		self.RFunctionParamse_scale_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "se_scale:")
		self.RFunctionParamscale_sd_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "scale_sd:")
		self.RFunctionParamprior_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "prior:")
		self.RFunctionParamthreshold_scale_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "threshold_scale:")
		self.RFunctionParamthreshold_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "threshold:")
		self.RFunctionParamsign_contrast_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "sign_contrast:")
		redRGUI.button(self.controlArea, label="Commit", callback = self.commitFunction)
		redRGUI.button(self.controlArea, label="Report", callback = self.sendReport)
	def processdata(self, data):
		self.require_librarys(["pamr"]) 
		if data:
			self.RFunctionParam_data=data["data"]
			self.commitFunction()
	def processgene_subset(self, data):
		self.require_librarys(["pamr"]) 
		if data:
			self.RFunctionParam_gene_subset=data["data"]
			self.commitFunction()
	def commitFunction(self):
		if str(self.RFunctionParam_data) == '': return
		if str(self.RFunctionParam_gene_subset) == '': return
		injection = []
		if str(self.RFunctionParamngroup_survival_lineEdit.text()) != '':
			string = 'ngroup_survival='+str(self.RFunctionParamngroup_survival_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamn_threshold_lineEdit.text()) != '':
			string = 'n_threshold='+str(self.RFunctionParamn_threshold_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamoffset_percent_lineEdit.text()) != '':
			string = 'offset_percent='+str(self.RFunctionParamoffset_percent_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamhetero_lineEdit.text()) != '':
			string = 'hetero='+str(self.RFunctionParamhetero_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamremove_zeros_lineEdit.text()) != '':
			string = 'remove_zeros='+str(self.RFunctionParamremove_zeros_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamsample_subset_lineEdit.text()) != '':
			string = 'sample_subset='+str(self.RFunctionParamsample_subset_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamse_scale_lineEdit.text()) != '':
			string = 'se_scale='+str(self.RFunctionParamse_scale_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamscale_sd_lineEdit.text()) != '':
			string = 'scale_sd='+str(self.RFunctionParamscale_sd_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamprior_lineEdit.text()) != '':
			string = 'prior='+str(self.RFunctionParamprior_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamthreshold_scale_lineEdit.text()) != '':
			string = 'threshold_scale='+str(self.RFunctionParamthreshold_scale_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamthreshold_lineEdit.text()) != '':
			string = 'threshold='+str(self.RFunctionParamthreshold_lineEdit.text())
			injection.append(string)
		if str(self.RFunctionParamsign_contrast_lineEdit.text()) != '':
			string = 'sign_contrast='+str(self.RFunctionParamsign_contrast_lineEdit.text())
			injection.append(string)
		inj = ','.join(injection)
		self.R(self.Rvariables['pamr.train']+'<-pamr.train(data='+str(self.RFunctionParam_data)+',gene.subset='+str(self.RFunctionParam_gene.subset)+','+inj+')')
		self.rSend("pamr.train Output", {"data":self.Rvariables["pamr.train"]})
	def compileReport(self):
		self.reportSettings("Input Settings",[("data", self.RFunctionParam_data)])
		self.reportSettings("Input Settings",[("gene_subset", self.RFunctionParam_gene_subset)])
		self.reportSettings('Function Settings', [('ngroup_survival',str(self.RFunctionParam_ngroup_survival))])
		self.reportSettings('Function Settings', [('n_threshold',str(self.RFunctionParam_n_threshold))])
		self.reportSettings('Function Settings', [('offset_percent',str(self.RFunctionParam_offset_percent))])
		self.reportSettings('Function Settings', [('hetero',str(self.RFunctionParam_hetero))])
		self.reportSettings('Function Settings', [('remove_zeros',str(self.RFunctionParam_remove_zeros))])
		self.reportSettings('Function Settings', [('sample_subset',str(self.RFunctionParam_sample_subset))])
		self.reportSettings('Function Settings', [('se_scale',str(self.RFunctionParam_se_scale))])
		self.reportSettings('Function Settings', [('scale_sd',str(self.RFunctionParam_scale_sd))])
		self.reportSettings('Function Settings', [('prior',str(self.RFunctionParam_prior))])
		self.reportSettings('Function Settings', [('threshold_scale',str(self.RFunctionParam_threshold_scale))])
		self.reportSettings('Function Settings', [('threshold',str(self.RFunctionParam_threshold))])
		self.reportSettings('Function Settings', [('sign_contrast',str(self.RFunctionParam_sign_contrast))])
		self.reportRaw(self.Rvariables["pamr.train"])
	def sendReport(self):
		self.compileReport()
		self.showReport()
