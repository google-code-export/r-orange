#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from OWWidget import *

import rpy2.robjects as robjects

class OWRpy():
	#a class variable which is incremented every time OWRpy is instantiated.
	
	num_widgets = 0
	def __init__(self):	
		#The class variable is used to create the unique names in R
		OWRpy.num_widgets += 1
		#this should be appended to every R variable
		self.variable_suffix = '_' + str(OWRpy.num_widgets)
		#create easy access to the R object
		self.r = robjects.r
		
	#convert R data.frames to Orange exampleTables
	def convertDataframeToExampleTable(self, dataFrame_name):
		isNA = self.r('is.na')
		dataFrame = self.r[dataFrame_name]
		col_def = [x for x in self.r.sapply(dataFrame,'class')]
		colClasses = []
		factors = {}
		for i in range(len(col_def)):
			if col_def[i] == 'numeric' or col_def[i] == 'integer':
				colClasses.append(orange.FloatVariable(dataFrame.colnames()[i]))
			elif col_def[i] == 'factor':
				colClasses.append(orange.StringVariable(dataFrame.colnames()[i]))
				factors[i] = [x for x in self.r.levels(dataFrame[i])]
			elif col_def[i] == 'character':
				colClasses.append(orange.StringVariable(dataFrame.colnames()[i]))
		d = []
		for x in range(dataFrame.nrow()):
			tmp = self.r(dataFrame_name + '[' + str(x+1) + ',]')
			row = []
			for y in range(tmp.ncol()):
				if isNA(tmp[y][0])[0]:
					row.append('?')
				else:
					if col_def[y] == 'factor':
						row.append(factors[y][tmp[y][0]-1])
					else:
						row.append(tmp[y][0])
			d.append(row)
		
		#data = [[x for x in y] for y in dataFrame]
		domain = orange.Domain(colClasses)
		data = orange.ExampleTable(domain, d)		
		return data
		