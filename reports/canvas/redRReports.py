import datetime, os, re
import redREnviron
from docutils.core import publish_string
from docutils.writers.odf_odt import Writer, Reader
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRExceptionHandling
import shutil

from libraries.base.qtWidgets.widgetBox import widgetBox as redRWidgetBox
from libraries.base.qtWidgets.groupBox import groupBox as redRGroupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel as redRwidgetLabel
from libraries.base.qtWidgets.listBox import listBox as redRlistBox
from libraries.base.qtWidgets.button import button as redRbutton
from libraries.base.qtWidgets.dialog import dialog as redRdialog

def createTable(arrayOfArray,tableName='', columnNames=None):
    # print len(arrayOfArray), len(arrayOfArray[0]), arrayOfArray
    if len(arrayOfArray) == 0 or len(arrayOfArray[0]) == 0:
        return '';
    if columnNames:
        headers = '  :header: "' + '","'.join(columnNames) + '"'
    else:
        headers = '';

    body = ''
    toAppend = []
    for row in arrayOfArray:
        formatted = []
        for cell in row:
            if type(cell) is not str:
                cell = str(cell)
                print cell
            if re.search('.. csv-table::|.. image::|::', cell):
                toAppend.append([row[0],cell])
                formatted.append('See Below')
            else:
                formatted.append(cell)
        
        body += '  "' + '","'.join(formatted) + '"\n'

    body += '\n\n'
    for x in toAppend:
        body += x[0] + '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n'
        body += x[1] + '\n\n'
        
    text = """
.. csv-table:: %s
%s

%s

""" % (tableName, headers, body)
    return text
    
def createLitralBlock(text):
    if text =='':
        return ''
    else:
        return "::\n\n  " + re.sub(r'\n','\n  ', text)

class reports(QDialog):
    def __init__(self,parent, schema):
        self.schema = schema
        
        QDialog.__init__(self, parent)
        self.setWindowTitle('Report Widget Selector')
        
        self.setLayout(QVBoxLayout())
        layout = self.layout()
        
        mainWidgetBox = redRWidgetBox(self)

        topWidgetBox = redRWidgetBox(mainWidgetBox)
        redRwidgetLabel(topWidgetBox,label='Select the widgets to include in the report.')
        
        self.widgetList = redRlistBox(topWidgetBox)
        self.widgetList.setSelectionMode(QAbstractItemView.MultiSelection)
        buttonWidgetBox = redRWidgetBox(mainWidgetBox,orientation='horizontal')
        
        acceptButton = redRbutton(buttonWidgetBox, 'Compile Report')
        QObject.connect(acceptButton, SIGNAL("clicked()"), self.accept)
        # QObject.connect(self.widgetList, SIGNAL("itemClicked(QListWidgetItem *)"), self.widgetListItemClicked)

        
    def widgetListItemClicked(self, item):
        itemText = str(item.text())
        self.widgetNames[itemText]['widget'].instance.includeInReport.setChecked(item.isSelected())
        
    def updateWidgetList(self,widgets):
        #topWidgetBox.layout().addWidget(self.widgetList)
        
        self.widgetNames = {}
        for widget in widgets:
            self.widgetNames[widget.caption] = {'inReport': widget.instance.includeInReport.isChecked(), 'widget':widget}
        #print self.widgetNames.keys()
        self.widgetList.clear()
        self.widgetList.addItems(self.widgetNames.keys())
        count = int(self.widgetList.count())
        
        for i in range(count):
            item = self.widgetList.item(i)
            if self.widgetNames[str(item.text())]['inReport']:
                self.widgetList.setItemSelected(item, True)

    def createReportsMenu(self):
        qname = QFileDialog.getSaveFileName(self, "Write Report to File", 
        redREnviron.directoryNames['documentsDir'] + "/Report-"+str(datetime.date.today())+".odt", 
        "Open Office Text (*.odt);; HTML (*.html);; LaTeX (*.tex)")
        if qname.isEmpty(): return
        qname = str(qname.toAscii())
        
        name = str(qname) # this is the file name of the Report
        if os.path.splitext(name)[1].lower() not in [".odt", ".html", ".tex"]: name = name + '.odt'
        fileDir = os.path.split(name)[0]
        try:
            fileDir2 = os.path.join(fileDir, os.path.splitext("Data-"+os.path.split(name)[1])[0])
            fileDir2 = fileDir2.replace('\\', '/')
            fd3 = []
            for p in fileDir2.split('/'):
                if len(p) > 8 and ' ' in p:
                    fd3.append(p.replace(' ', '')[:6]+'~1')
                else:
                    fd3.append(p)
            fileDir2 = '/'.join(fd3)
            if os.path.isdir(fileDir2):
                shutil.rmtree(fileDir2)

            # makes a file to place the temp data into.  
            #This will be deleted once the odt file is made.
            os.mkdir(fileDir2)  
        
        except Exception as inst:
            print redRExceptionHandling.formatException()
        
        
        # show the report list and allow the user to select widgets to include in the report.
        ## get the report info for the included widgets.

        self.updateWidgetList(self.schema.widgets)
        if self.exec_() == QDialog.Rejected:
            return

        self.createReport(fileDir2,name)
        
        if os.name =='nt':
            #os.startfile
            doneDialog = redRdialog(self.schema,title="Report Generated")
            redRwidgetLabel(doneDialog,label='Your report is ready to view.')
            buttonBox = redRWidgetBox(doneDialog,orientation='horizontal')
            acceptButton = redRbutton(buttonBox,'View Report')
            QObject.connect(acceptButton, SIGNAL("clicked()"), doneDialog.accept)
            acceptButton = redRbutton(buttonBox,'Done')
            QObject.connect(acceptButton, SIGNAL("clicked()"), doneDialog.reject)
            if doneDialog.exec_() == QDialog.Accepted:
                os.startfile(name,'open')
        else:
            QMessageBox.information(self, "Red-R Canvas", "Your report is ready to view.", 
            QMessageBox.Ok + QMessageBox.Default )    
    def createReport(self,fileDir,reportName):
        
        reportText = self.buildReportHeader(fileDir)
        
        ## very simply we need to loop through the widgets and get some info 
        ## about them and put that into the report.
        toInclude = self.widgetList.getCurrentSelection()
        for widget in toInclude:
            reportText += self.getWidgetReport(fileDir, self.widgetNames[widget]['widget'])
        
        
        # file = open(str(os.path.join(fileDir, 'content.rst')).replace('\\','/'), "wt")
        # file.write(reportText)
        # file.close()
        
        # print '############################\n'*5
        # print reportText
        # print '############################\n'*5
        
        if os.path.splitext(str(reportName))[1].lower() in [".odt"]:#, ".html", ".tex"]
            reader = Reader()
            writer = Writer()
            output = publish_string(reportText, reader = reader, writer = writer)
            file = open(reportName, 'wb')
            file.write(output)
            file.close()
            shutil.rmtree(fileDir)

            
            
        elif os.path.splitext(str(reportName))[1].lower() in [".tex"]:# , ".tex"]
            output = publish_string(reportText, writer_name='latex')#, writer = writer, reader = reader)
            file = open(reportName, 'w')
            file.write(output)
            file.close()
        elif os.path.splitext(str(reportName))[1].lower() in [".html"]:# , ".tex"]
            output = publish_string(reportText, writer_name='html')
            # print output
            # print type(output)
            # print str(output)
            file = open(reportName, 'w')
            file.write(output)
            file.close()
            
        
    def buildReportHeader(self,fileDir):
       ## first take a picture of the canvas and save as png.
        image = QImage(1000, 700, QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        self.schema.canvasView.scene().render(painter) #
        painter.end()
        imageFile = os.path.join(fileDir, 'canvas-image.png').replace('\\', '/')
        if not image.save(imageFile):
            print 'Error in saving schema'
            print image
            print image.width(), 'width'

        text = """
===========================================
 Red-R Report
===========================================
:Date: %s

.. contents::
.. sectnum::

Schema
========
.. image:: %s
  :scale: 50%% 

""" % (datetime.date.today(), imageFile)


        # text = '**Red-R Report compiled on '+str(datetime.date.today())+'**\n\n'
        # text += 'Schema Image\n\n'
        # text += '.. image:: %s\n  :scale: 50%%\n' % (imageFile)
        # text += ''
        # text += '\n\n\n--------------------\n\n\n'

        return text;

    def getWidgetReport(self, fileDir, widget):

        notes = widget.instance.notes.getReportText(fileDir)
        if notes['text'] =='':
            notes = 'No notes were entered in the widget face.'
        else:
            notes = notes['text']
        # print widget.instance._widgetInfo.widgetName
        widgetOutput = widget.instance.getReportText3(fileDir)
        tt = """
%s
================================================

Notes
-----

%s

Widget Output
-------------

%s

""" % (widget.caption, notes, widgetOutput)

        return tt

        # tt = '\n%s\n%s\n'%(widget.caption, '))))))))))))))))))))))))))))))))))))')
        # try:
            # tt += widget.instance.getReportText(fileDir)
            # tt += '\n\n\n--------------------\n\n\n'
            # tt += '\n\n%s\n%s\n\n'%('Notes', '>>>>>>>>>>>>>>>>>>>>>>>>')
            # if str(widget.instance.notes.toPlainText()) != '':
                # tt += str(r'\n'+widget.instance.notes.toPlainText()).replace(r'\n', r'\n\t')+'\n\n'
            # else:
                # tt += 'No notes were entered in the widget face.\n\n'
            # tt += '\n\n\n--------------------\n\n\n'
            # tt += '\n\n%s\n%s\n\n'%('Signals', '>>>>>>>>>>>>>>>>>>>>>>>>')
            # try:
                # if widget.instance.inputs:
                    
                    # for input in widget.instance.inputs:
                        # for iwidget in self.signalManager.getLinkWidgetsIn(widget.instance, input[0]):
                            # tt += '-The Signal *%s* is linked to widget *%s*\n\n' % (input[0], iwidget.captionTitle)
            # except: pass
            # try:
                # if widget.instance.outputs:
                    ##tt += '</br><strong>The following widgets are sent from this widget:</strong></br>'
                    # for output in widget.instance.outputs:
                        # for owidget in self.signalManager.getLinkWidgetsOut(widget.instance, output[0]):
                            # tt += '-This widget sends the signal *%s* to widget *%s*\n\n' % (output[0], owidget.captionTitle)
            # except:
                # pass
        # except Exception as inst:
            # print '##########################'
            # print str(inst)
            # print '##########################'
            # tt += 'Error occured in report generation for this widget'
        # tt += '\n\n'
        
        
