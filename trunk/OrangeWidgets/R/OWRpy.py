#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from OWWidget import *
import os
from rpy_options import set_options
set_options(RHOME=os.environ['RPATH'])
import rpy
import time

class OWRpy(OWWidget):
    #a class variable which is incremented every time OWRpy is instantiated.
    processing  = False
    num_widgets = 0
    def __init__(self):	
        #The class variable is used to create the unique names in R
        OWRpy.num_widgets += 1
        #this should be appended to every R variable
        self.variable_suffix = '_' + str(OWRpy.num_widgets)
        #keep all R variable name in this dict
        self.Rvariables = {}
        
        
    
    def rsession(self,query,processing_notice=False):
        if processing_notice:
            self.progressBarInit()
            self.progressBarSet(30)
        print query
        output  = rpy.r(query)
        OWRpy.processing = False
        if processing_notice:
            self.progressBarFinished()
        return output
        # print 'in rssion:' + str(OWRpy.processing)
        # while True:
            # if not OWRpy.processing:
                # OWRpy.processing = True
                # print query
                # output  = rpy.r(query)
                # OWRpy.processing = False
                # print 'done'
                # return output
            # else:
                # return
                # print 'asdf'
                # OWRpy.processing = False
                
            
    def require_librarys(self,librarys):
        for library in librarys:
            print self.rsession("library('"+ library +"',logical.return=T)") == False
            if not self.rsession("library('"+ library +"',logical.return=T)"): 
                self.rsession('setRepositories(ind=1:7)')
                self.rsession('chooseCRANmirror()')
                self.rsession('install.packages("' + library + '")')
                
            self.rsession('require('  + library + ')')
    
    def setRvariableNames(self,names):
        dict = {}
        for x in names:
            dict[x] = x + self.variable_suffix
        return dict
            
    #convert R data.frames to Orange exampleTables
    def convertDataframeToExampleTable(self, dataFrame_name):
        #set_default_mode(CLASS_CONVERSION)

        dataFrame = self.rsession(dataFrame_name)	
        col_names = self.rsession('colnames(' + dataFrame_name + ')')
        if self.rsession("class(" + dataFrame_name + ")") == 'matrix':
            col_def = self.rsession("apply(" + dataFrame_name + ",2,class)")
        else:
            col_def = self.rsession("sapply(" + dataFrame_name + ",class)")
        colClasses = []
        for i in col_names:
            if col_def[i] == 'numeric' or col_def[i] == 'integer':
                colClasses.append(orange.FloatVariable(i))
            elif col_def[i] == 'factor':
                colClasses.append(orange.StringVariable(i))
            elif col_def[i] == 'character':
                colClasses.append(orange.StringVariable(i))
            elif col_def[i] == 'logical':
                colClasses.append(orange.StringVariable(i))
            else:
                colClasses.append(orange.StringVariable(i))
                
        self.rsession('exampleTable_data' + self.variable_suffix + '<- '+ dataFrame_name)
        self.rsession('exampleTable_data' + self.variable_suffix + '[is.na(' + dataFrame_name + ')] <- "?"')

        d = self.rsession('as.matrix(exampleTable_data' + self.variable_suffix + ')')
        domain = orange.Domain(colClasses)
        data = orange.ExampleTable(domain, d)
        self.rsession('rm(exampleTable_data' + self.variable_suffix + ')')
        return data
        
    def onDeleteWidget(self):
        for k in self.Rvariables:
            print self.Rvariables[k]
            self.rsession('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }')
            

        