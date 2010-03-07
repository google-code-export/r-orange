"""
<name>getGEO</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Gets GEO data and brings it into the RedR session.  May have problems if a very large dataset is imported</description>
<tags>Bioinformatics</tags>
<RFunctions>GEOquery:getGEO</RFunctions>
<icon>icons/readcel.png</icon>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class getGEO(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["getGEO", "ExpressionSet"])
        self.RFunctionParam_destdir = "tempdir()"
        self.RFunctionParam_GEO = "NULL"
        self.RFunctionParam_GSEMatrix = "FALSE"
        self.RFunctionParam_GSElimits = "NULL"
        self.RFunctionParam_filename = "NULL"
        self.loadSettings() 
        self.outputs = [("getGEO Output", RvarClasses.RVariable)]
        
        box = RRGUI.tabWidget(self.controlArea, None, self)
        self.standardTab = RRGUI.createTabPage(box, "standardTab", self, "Standard")
        self.advancedTab = RRGUI.createTabPage(box, "advancedTab", self, "Advanced")
        self.RFUnctionParamdestdir_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamdestdir_lineEdit", self, "RFunctionParam_destdir", label = "destdir:")
        self.RFUnctionParamGEO_lineEdit =  RRGUI.lineEdit(self.standardTab, "RFUnctionParamGEO_lineEdit", self, "RFunctionParam_GEO", label = "GEO:")
        self.RFUnctionParamGSEMatrix_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamGSEMatrix_lineEdit", self, "RFunctionParam_GSEMatrix", label = "GSEMatrix:")
        self.RFUnctionParamGSElimits_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamGSElimits_lineEdit", self, "RFunctionParam_GSElimits", label = "GSElimits:")
        self.RFUnctionParamfilename_lineEdit =  RRGUI.lineEdit(self.advancedTab, "RFUnctionParamfilename_lineEdit", self, "RFunctionParam_filename", label = "filename:")
        OWGUI.button(self.controlArea, self, "Commit", callback = self.commitFunction)
    def commitFunction(self):
        self.require_librarys(['GEOquery', 'Biobase'])
        if self.RFunctionParam_GEO == '': return
        injection = []
        if self.RFunctionParam_GEO != '':
            string = '"'+str(self.RFunctionParam_GEO)+'"'
            injection.append(string)
        if self.RFunctionParam_destdir != '':
            string = 'destdir='+str(self.RFunctionParam_destdir)
            injection.append(string)
        if self.RFunctionParam_GSEMatrix != '':
            string = 'GSEMatrix='+str(self.RFunctionParam_GSEMatrix)
            injection.append(string)
        if self.RFunctionParam_GSElimits != '':
            string = 'GSElimits='+str(self.RFunctionParam_GSElimits)
            injection.append(string)
        if self.RFunctionParam_filename != '':
            string = 'filename='+str(self.RFunctionParam_filename)
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['getGEO']+'<-getGEO('+inj+')', silentErrors = 1, errorMessage = 'GEO query not responding, make sure that your query is correct.')
        if 'GSE' in self.R('class('+self.Rvariables['getGEO']+')'):
            #need to convert to an expression set
            if int(self.R('length(names(GPLList('+self.Rvariables['getGEO']+')))')) > 1: # there are two GPL types so we need to do something
                esetData = None
            else:
                tmp = self.Rvariables['getGEO']
                self.R('probesets<-Table(GPLList('+tmp+')[[1]])$ID')
                self.R('data.matrix<-log2(do.call("cbind", lapply(GSMList('+tmp+'), function(x){tab<-Table(x); mymatch <- match(probesets, tab$ID_REF); return(tab$VALUE[mymatch])})))')
                self.R('rownames(data.matrix)<-probesets')
                self.R('colnames(data.matrix)<-names(GSMList('+tmp+'))')
                self.R('pdata<-data.frame(samples = names(GSMList('+tmp+')))')
                self.R('rownames(pdata) <- names(GSMList('+tmp+'))')
                self.R('pheno<-new("AnnotatedDataFrame", pData = pdata, varLabels = as.list("samples"))')
                self.R(self.Rvariables['ExpressionSet']+'<-new("ExpressionSet", exprs = data.matrix, phenoData = pheno)')
                esetData = {"data":self.Rvariables['ExpressionSet']}
        elif 'GDS' in self.R('class('+self.Rvariables['getGEO']+')'):
            self.R(self.Rvariables['ExpressionSet']+'<-GDS2eSet('+self.Rvariables['getGEO']+', do.log2 = TRUE)')
            esetData = {"data":self.Rvariables['ExpressionSet']}
        self.rSend("getGEO Output", {"data":self.Rvariables["getGEO"]})
        self.rSend("Expression Set", esetData)
