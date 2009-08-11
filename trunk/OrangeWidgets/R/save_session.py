from OWRpy import *
from xml.dom.minidom import Document, parse
filename = 'asdf'
doc = Document()
Rdata = doc.createElement("Rdata")
d = open('G:/Python25/Lib/site-packages/orange/OrangeWidgets/R/RData', mode='rb')
tmp = d.read()
Rdata.setAttribute("data",tmp)
doc.appendChild(Rdata)
xmlText = doc.toprettyxml()

file = open(filename, "wt")
file.write(xmlText)
file.close()
doc.unlink()

myfile = open("test.RData", "wb")
myfile.write(tmp)
myfile.close()
