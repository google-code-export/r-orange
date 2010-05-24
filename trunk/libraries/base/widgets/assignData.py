## assign data from table widget author Kyle R Covington (kyle@red-r.org)
## this widget shows data in a table and allows one to assign classifications to those data.  basically like reshape but much more amorphic

"""
<name>Assign Data</name>
<description>Assign attributes to data and shift it into the "long" form.  This is useful if you have a matrix of data and want to assign it to some groupings.</description>
<tags>Data Classification</tags>
<RFunctions></RFunctions>
<icon></icon>
<priority>1010</priority>
"""


from OWRpy import *
# import OWGUI
import signals
import redRGUI 


class assignData(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, 'Assign Data')
        
        ## settings ##
        self.inAssignmentMode = 0
        self.attsCounter = 0
        ## data holders
        self.data = {}  ## the holder for the data that is brought in, multiple tables can be attached.
        self.tableDict = {}  ## a dict of tables that have been attached.
        self.attributes = {} ## a holder for the attrubutes.  These will be specified by text, color, or other special things (contains dicts)
        self.attsDict = {}
        self.setRvariableNames(['longTable'])
        ## inputs and outputs
        self.inputs = [('Data', signals.StructuredDict, self.gotData, 'Multiple')]
        self.outputs = [('Reshaped Data', signals.rsqlitedataframe.SQLiteTable)]
        
        ## GUI ##
        
        fullArea = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        leftArea = redRGUI.widgetBox(fullArea, orientation = 'vertical')
        topArea = redRGUI.widgetBox(leftArea, orientation = 'horizontal')
        rightArea = redRGUI.widgetBox(fullArea, orientation = 'vertical')
        rightArea.setMaximumWidth(150)
        
        
        #### make the scroll area ####
        groupArea = redRGUI.groupBox(topArea, label = 'Groupings')
        self.groupScrollArea = QScrollArea()
        
        groupArea.layout().addWidget(self.groupScrollArea)
        
        self.groupScrollAreaLayout = QWidget()  ## the scroll area of the groupbox, we can put more widgets into this to assign groupings
        self.groupScrollAreaLayout.setLayout(QHBoxLayout())
        self.groupScrollArea.setWidget(self.groupScrollAreaLayout)
        self.groupScrollAreaLayout.show()
        self.groupScrollArea.setWidgetResizable(True)
        
        assignButtonArea = redRGUI.widgetBox(topArea, orientation = 'vertical')
        self.addAttributeButton = redRGUI.button(assignButtonArea, label = 'Add Attribute', callback = self.addAttribute)
        self.assignButton = redRGUI.button(assignButtonArea, label = 'Assign', callback = self.startAssignment)
        self.commitAssignmentButton = redRGUI.button(assignButtonArea, label = 'Commit Assignment', callback = self.commitAssignment)
        commitAllAssignmentsButton = redRGUI.button(assignButtonArea, label = 'Send commitments', callback = self.commitAllAssignments)
        
        #### make the table area (we'll have to populate the table in this widget since we are using a custom class)
        tableArea = redRGUI.groupBox(leftArea, label = 'Table Area')
        self.tableTabs = redRGUI.tabWidget(tableArea)
        
        #### make the attribute area, this will be on the right hand side selecting these will load the settings into the groupScrollArea settings.
        attsArea = redRGUI.groupBox(rightArea, label = 'Attributes')
        self.attributesListBox = redRGUI.listBox(attsArea, toolTip = 'Click on an attribute to repopulate it in the groups area.', callback = self.reloadGroupArea)

    def gotData(self, data, id):
        print id
        if data:
            self.data[id] = data
            self.tableDict[id] = {}
            self.assignTable(data, id)
            
    def assignTable(self, data, id):
        ## want to make a tab for the table this should be numeric something like table 1 and then place a table into that tab with the data that we got in data.
        self.tableDict[id]['tab'] = self.tableTabs.createTabPage(str(id))
        self.tableDict[id]['table'] = redRGUI.table(self.tableDict[id]['tab'], callback = lambda r, c, id = id: self.cellClicked(r, c, id))
        self.tableDict[id]['table'].setTable(data.getData(), data.getItem('keys'))  ## set the table
    def cellClicked(self, r, c, id):
        print r, c, id
        if self.inAssignmentMode:
            item = self.tableDict[id]['table'].item(int(r), int(c))
            if not item:  # in case we have a blank cell we still assign an item and an assignment (could be used for making a template classification table.
                newitem = QTableWidgetItem()
                self.tableDict[id]['table'].setItem(int(r), int(c), newitem)
                item = newitem
                item.attribute = None  # we make the slot to fill with data.
            try:
                a = item.attribute
            except:
                item.attribute = None
            if item.attribute and item.attribute == self.currentAttribute['group']:  # we need to clear the attribute from this item.
                item.attribute = None
                item.setBackgroundColor(Qt.white)
            else:
                item.attribute = self.currentAttribute['group']
                item.setBackgroundColor(self.currentAttribute['color'])
    def addAttribute(self):
        # add a widgetBox with tools to assign an attribute in the groupScrollArea
        mb = redRGUI.dialog(self)
        name = redRGUI.lineEdit(mb, label = 'Group Name', callback = mb.accept)
        if mb.exec_() == QDialog.Accepted:
            gname = str(name.text())
        else:
            return
        groupBox = redRGUI.groupBox(self.groupScrollAreaLayout, label = 'Attribute '+gname)
        groupBox.setMaximumWidth(175) ## we don't want the area being too large
        self.groupScrollArea.widget().show()
        lineEdit = redRGUI.lineEdit(groupBox, label = 'Attribute Name', toolTip = 'Add an attribute.', callback = lambda x = gname: self.addAttributeLabel(x))
        listBox = redRGUI.listBox(groupBox, label = 'Added Names', toolTip = 'These are attributes that you have already added.', callback = lambda y, x = gname: self.setAttributeLabel(y, x)) ## y is the item clicked, x is the gname of this widget
        
        self.attsDict[gname] = {'lineEdit':lineEdit, 'listBox':listBox}
    def setAttributeLabel(self, y, x):
        selectedItemText = str(y.text())
        self.attsDict[x]['lineEdit'].setText(selectedItemText)
        
    def addAttributeLabel(self, x):
        items = self.attsDict[x]['listBox'].items()
        text = str(self.attsDict[x]['lineEdit'].text())
        for i in items:
            if str(i.text()) == text:
                self.attsDict[x]['listBox'].setItemSelected(i)
                return
                
        self.attsDict[x]['listBox'].addItem(text)
    def startAssignment(self):
        ## make an assignment grouping and a color grouping
        self.assignButton.setEnabled(False)
        self.commitAssignmentButton.setEnabled(True)
        groupingDict = {}
        for name in self.attsDict.keys():
            ## get the text for the name
            text = str(self.attsDict[name]['lineEdit'].text())
            groupingDict[name] = text  # make a grouping dict that we can assign to things.
            
        for att in self.attributes.keys():
            if self.attributes[att]['group'] == groupingDict:
                self.currentAttribute = self.attributes[att]
                self.inAssignmentMode = 1
                return
        colorDialog = QColorDialog(self)
        color = colorDialog.getColor()
        colorDialog.hide()
        
        self.attributes[self.attsCounter] = {'group':groupingDict, 'color':color}
        self.currentAttribute = self.attributes[self.attsCounter]
        
        attributesListItem = QListWidgetItem(str(groupingDict))
        attributesListItem.setBackgroundColor(color)
        self.attributesListBox.addItem(attributesListItem)
        
        self.attsCounter += 1
        self.inAssignmentMode = 1
    def commitAssignment(self):
        self.inAssignmentMode = 0
        self.commitAssignmentButton.setEnabled(False)
        self.assignButton.setEnabled(True)
    def reloadGroupArea(self):
        pass
    def commitAllAssignments(self):
        self.Rvariables['longTable'] = self.Rvariables['longTable'].replace('.', '_')
        # move across all of the tables and make the commitments.  
        database = os.path.join(qApp.canvasDlg.tempDir, 'temp.db')
        keys = self.attsDict.keys()
        for i in range(len(keys)):
            if type(keys[i]) == str:
                keys[i] = keys[i].replace(' ', '_')
                keys[i] = keys[i].replace('.', '_')
        ## how many ? to add
        questions = []
        for k in ['row_names'] + keys + ['Table_values']:
            questions.append('?')
        ## collect all of the data to insert
        rowName = 0
        insertData = []
        for id in self.tableDict.keys(): ## move across all of the tables
            for r in range(self.tableDict[id]['table'].rowCount()):  ## move across all of the rows
                for c in range(self.tableDict[id]['table'].columnCount()):  ## move across all of the columns
                    j = [rowName]
                    
                    item = self.tableDict[id]['table'].item(r, c)
                    try:
                        if item.attribute == None:  ## ignore those attributes that are None
                            continue
                    except AttributeError:
                        continue
                    for key in keys:
                        j.append(item.attribute[key])
                    try:
                        j.append(float(item.text()))
                    except:
                        j.append(str(item.text()))

                    insertData.append(tuple(j))
                    rowName += 1
        import sqlite3
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        ## drop the table if one is already in the database
        cursor.execute('DROP TABLE IF EXISTS '+self.Rvariables['longTable'])
        createTablestr = 'CREATE TABLE '+self.Rvariables['longTable']+'("'+'","'.join(['row_names']+keys+['Table_values'])+'")'
        try:
            cursor.execute(createTablestr)
        except Exception as inst:
            print inst
            print createTablestr
            conn.close()
            raise Exception
            
        insertDataStr = 'INSERT INTO '+self.Rvariables['longTable']+' ("'+'","'.join(['row_names'] + keys + ['Table_values'])+'") values ('+','.join(questions)+')'
        try:
            cursor.executemany(insertDataStr, insertData)
        except Exception as inst:
            print inst
            print insertDataStr
            conn.close()
            raise Exception
        conn.commit()
        conn.close()
        
        sendData = signals.rsqlitedataframe.SQLiteTable(data = str(self.Rvariables['longTable']), database = 'local|temp.db')
        self.rSend('Reshaped Data', sendData)