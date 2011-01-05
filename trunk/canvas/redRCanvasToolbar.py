import redREnviron,redRStyle, redRObjects, redRSaveLoad, redRGUI,signals, orngDlgs, orngRegistry
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, sys
from libraries.base.qtWidgets.SearchDialog import SearchDialog as redRSearchDialog
from libraries.base.qtWidgets.lineEditHint import lineEditHint as redRlineEditHint
from libraries.base.qtWidgets.widgetBox import widgetBox as redRwidgetBox

class redRCanvasToolbarandMenu():
    def __init__(self,canvas,toolbar):
        self.canvas = canvas
        self.toolbar = toolbar
        self.menuSaveSettingsID = -1
        self.menuSaveSettings = 1
        self.originalPalette = QApplication.palette()
        self.recentDocs = []
        ###############################
        self.initMenu()
        self.initToolbar()
        
    def initToolbar(self):
        self.toolbar.setOrientation(Qt.Horizontal)
        if not redREnviron.settings.get("showToolbar", True): self.toolbar.hide()
        self.toolbar.addAction(QIcon(redRStyle.openFileIcon), "Open schema", self.menuItemOpen)
        self.toolSave = self.toolbar.addAction(QIcon(redRStyle.saveFileIcon), "Save schema", self.menuItemSave)
        #self.toolReloadWidgets = self.toolbar.addAction(QIcon(redRStyle.reloadIcon), "Reload Widgets", self.reloadWidgets)
        # self.toolbar.addAction(QIcon(redRStyle.showAllIcon), "Show All Widget Windows", redRObjects.showAllWidgets)
        # self.toolbar.addAction(QIcon(redRStyle.closeAllIcon), "Close All Widget Windows", redRObjects.closeAllWidgets)
        # self.toolbar.addSeparator()
        # self.toolbar.addAction(QIcon(redRStyle.printIcon), "Print", self.menuItemPrinter)

        self.toolbar.addSeparator()
        self.toolbar.addAction(QIcon(redRStyle.showAllIcon), "Show All Widget Windows", 
        redRObjects.showAllWidgets)
        self.toolbar.addAction(QIcon(redRStyle.closeAllIcon), "Close All Widget Windows", 
        redRObjects.closeAllWidgets)
        
        self.toolbar.addSeparator()
        self.toolbar.addAction(QIcon(redRStyle.printIcon), "Generate Report", self.menuItemReport)
        
        self.toolbar.addSeparator()
        self.toolbar.addAction(QIcon(redRStyle.updateIcon), 
        "Check for Updates", self.menuCheckForUpdates)
        
        self.toolbar.addSeparator()
        self.toolReloadWidgets = self.toolbar.addAction(QIcon(redRStyle.reloadIcon), 
        "Reload Widgets", self.reloadWidgets)
        self.toolbar.addSeparator()
        self.toolReloadWidgets = self.toolbar.addAction(QIcon(redRStyle.optionsIcon), 
        "Red-R Options", self.menuItemCanvasOptions)

        space = redRwidgetBox(None)
        space.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(space)
        
        self.widgetSuggestEdit = SearchBox(None, width=300)
        self.toolbar.addWidget(QLabel('Search  '))
        self.toolbar.addWidget(self.widgetSuggestEdit)
        
        
        self.readShortcuts()
        self.readRecentFiles()
        
        
    def initMenu(self):
        self.menuRecent = QMenu("Recent Schemas", self.canvas)

        self.menuFile = QMenu("&File", self.canvas)
        self.menuFile.addAction( "New Schema",  self.menuItemNewScheme, QKeySequence.New)
        self.menuFile.addAction(QIcon(redRStyle.openFileIcon), "&Open...", self.menuItemOpen, QKeySequence.Open )
        self.menuFile.addAction(QIcon(redRStyle.openFileIcon), "&Open and Freeze...", self.menuItemOpenFreeze)
        self.menuFile.addAction("Import Schema", self.importSchema)
        if os.path.exists(os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "lastSchema.tmp")):
            self.menuFile.addAction("Reload Last Schema", self.menuItemOpenLastSchema, Qt.CTRL+Qt.Key_R)
        #self.menuFile.addAction( "&Clear", self.menuItemClear)
        self.menuFile.addSeparator()
        self.menuSaveID = self.menuFile.addAction(QIcon(redRStyle.saveFileIcon), "&Save", self.menuItemSave, QKeySequence.Save )
        self.menuSaveAsID = self.menuFile.addAction( "Save &As...", self.menuItemSaveAs)
        self.menuSaveTemplateID = self.menuFile.addAction( "Save As Template", self.menuItemSaveTemplate)
        self.menuFile.addSeparator()
        #self.menuFile.addAction(QIcon(redRStyle.printIcon), "Print Schema / Save image", self.menuItemPrinter, QKeySequence.Print )
        self.menuFile.addAction("Compile &Report", self.menuItemReport)
        self.menuFile.addSeparator()
        self.menuFile.addMenu(self.menuRecent)
        self.menuFile.addSeparator()
        self.menuFile.addAction( "E&xit",  self.canvas.close, Qt.CTRL+Qt.Key_Q )

        self.menuOptions = QMenu("&Options", self.canvas)
        self.menuOptions.addAction( "Enable All Links",  self.menuItemEnableAll, Qt.CTRL+Qt.Key_E)
        self.menuOptions.addAction( "Disable All Links",  self.menuItemDisableAll, Qt.CTRL+Qt.Key_D)
        self.menuOptions.addAction( "Select All Widgets", self.selectAllWidgets, Qt.CTRL+Qt.Key_A)
        #self.menuOptions.addAction("New Tab", self.canvas.schema.newTab)
        self.menuOptions.addSeparator()
        self.menuOptions.addAction("Show Output Window", self.menuItemShowOutputWindow)
        self.menuOptions.addAction("Clear Output Window", self.menuItemClearOutputWindow)
        self.menuOptions.addAction("Save Output Text...", self.menuItemSaveOutputWindow)

        self.menuTabs = QMenu("&Tabs", self.canvas)
        self.menuTabs.addAction("Add New Tab", self.canvas.schema.newTab)
        self.menuTabs.addAction("Remove Current Tab", self.canvas.schema.removeCurrentTab)
        # uncomment this only for debugging
        #self.menuOptions.addSeparator()
        #self.menuOptions.addAction("Dump widget variables", self.dumpVariables)

        self.menuOptions.addSeparator()
        #self.menuOptions.addAction( "Channel preferences",  self.menuItemPreferences)
        #self.menuOptions.addSeparator()
        # self.menuOptions.addAction( "&Customize Shortcuts",  self.menuItemEditWidgetShortcuts)
        self.menuOptions.addAction( "&Delete Widget Settings",  self.menuItemDeleteWidgetSettings)
        self.menuOptions.addSeparator()
        self.menuOptions.addAction( sys.platform == "darwin" and "&Preferences..." or "Canvas &Options...",  self.menuItemCanvasOptions)

        self.packageMenu = QMenu("&Packages", self.canvas)
        self.packageMenu.addAction("Package Manager", self.menuOpenPackageManager)
        self.packageMenu.addAction(QIcon(redRStyle.openFileIcon), "&Install Package", self.menuItemInstallPackage)

        localHelp = 0
        self.menuHelp = QMenu("&Help", self.canvas)
        
        if os.path.exists(os.path.join(redREnviron.directoryNames['redRDir'], r"doc/reference/default.htm")) or os.path.exists(os.path.join(redREnviron.directoryNames['redRDir'], r"doc/canvas/default.htm")):
            if os.path.exists(os.path.join(redREnviron.directoryNames['redRDir'], r"doc/reference/default.htm")): self.menuHelp.addAction("Red-R Help", self.menuOpenLocalOrangeHelp)
            if os.path.exists(os.path.join(redREnviron.directoryNames['redRDir'], r"doc/canvas/default.htm")): self.menuHelp.addAction("Red Canvas Help", self.menuOpenLocalCanvasHelp)

        self.menuHelp.addAction("Red-R Online Help", self.menuOpenOnlineOrangeHelp)
        #self.menuHelp.addAction("Orange Canvas Online Help", self.menuOpenOnlineCanvasHelp)

        if os.path.exists(os.path.join(redREnviron.directoryNames['redRDir'], r"updateOrange.py")):
            self.menuHelp.addSeparator()
            self.menuHelp.addAction("Check for updates", self.menuCheckForUpdates)
            
        self.menuHelp.addSeparator()
        self.menuHelp.addAction("About Red-R", self.menuItemAboutOrange)

        # widget popup menu
        self.widgetPopup = QMenu("Widget", self.canvas)
        self.widgetPopup.addAction("Open",  self.canvas.schema.activeTab().openActiveWidget)
        self.widgetPopup.addSeparator()
        rename = self.widgetPopup.addAction( "&Rename", self.canvas.schema.activeTab().renameActiveWidget, Qt.Key_F2)
        delete = self.widgetPopup.addAction("Remove", self.canvas.schema.activeTab().removeActiveWidget, Qt.Key_Delete)
        #copy = self.menuTabs.addAction("&Copy", redRSaveLoad.collectIcons, Qt.CTRL+Qt.Key_C)
        cloneToTab = self.menuTabs.addAction("Clone To Tab", self.canvas.schema.cloneToTab, Qt.CTRL+Qt.Key_G)
        duplicateToTab = self.menuTabs.addAction("Duplicate To Tab", redRSaveLoad.copy, Qt.CTRL+Qt.Key_H)
        
        self.widgetPopup.setEnabled(0)
        self.canvas.widgetPopup = self.widgetPopup

        self.menuBar = QMenuBar(self.canvas)
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuOptions)
        self.menuBar.addMenu(self.menuTabs)
        self.menuBar.addMenu(self.widgetPopup)
        self.menuBar.addMenu(self.packageMenu)
        self.menuBar.addMenu(self.menuHelp)
        self.canvas.setMenuBar(self.menuBar)
    
    
    def readShortcuts(self):
        self.widgetShortcuts = {}
        shfn = os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "shortcuts.txt")
        if os.path.exists(shfn):
            for t in file(shfn).readlines():
                key, info = [x.strip() for x in t.split(":")]
                if len(info)== 0: continue
                if info[0] == "(" and info[-1] == ")":
                    cat, widgetName = eval(info)            # new style of shortcuts are of form F: ("Data", "File")
                else:
                    cat, widgetName = info.split(" - ")   # old style of shortcuts are of form F: Data - File
                if self.widgetRegistry.has_key(cat) and self.widgetRegistry[cat].has_key(widgetName):
                    self.widgetShortcuts[key] = self.widgetRegistry[cat][widgetName]

    def importSchema(self):
        name = QFileDialog.getOpenFileName(self.canvas, "Import File", redREnviron.settings["saveSchemaDir"], "Red-R Widget Schema (*.rrs *.rrts)")
        if name.isEmpty(): return
        name = unicode(name)
        
        name = unicode(name)
        
        redREnviron.settings['saveSchemaDir'] = os.path.split(unicode(name))[0]
        self.canvas.schema.loadDocument(unicode(name), freeze = 0, importing = True)
        self.addToRecentMenu(unicode(name))
        
    def menuItemOpen(self):
        name = QFileDialog.getOpenFileName(self.canvas, "Open File", 
        redREnviron.settings["saveSchemaDir"], "Schema or Template (*.rrs *.rrts)")
        
        if name.isEmpty(): return
        name = unicode(name)
        
        redREnviron.settings['saveSchemaDir'] = os.path.split(unicode(name))[0]
        self.canvas.schema.clear()
        redRSaveLoad.loadDocument(unicode(name), freeze = 0, importing = False)
        self.addToRecentMenu(unicode(name))


    def menuItemOpenFreeze(self):
        name = QFileDialog.getOpenFileName(self.canvas, "Open File", 
        redREnviron.settings["saveSchemaDir"], "Schema or Template (*.rrs *.rrts)")
        if name.isEmpty(): return
        name = unicode(name)
        
        self.canvas.schema.clear()
        self.canvas.schema.loadDocument(unicode(name), freeze = 1)
        self.addToRecentMenu(unicode(name))


    def menuItemOpenLastSchema(self):
        fullName = os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "lastSchema.tmp")
        if os.path.exists(fullName):
            self.canvas.schema.loadDocument(fullName)

    def menuItemSave(self):
        redRSaveLoad.saveDocumentAs()
    def reloadWidgets(self): # should have a way to set the desired tab location 
        
        self.widgetRegistry = orngRegistry.readCategories()
        redREnviron.addOrangeDirectoriesToPath(redREnviron.directoryNames)
        signals.registerRedRSignals()
        redRGUI.registerQTWidgets()
        
        self.canvas.createWidgetsToolbar(self.widgetRegistry)
        
        
    def menuItemSaveAs(self):
        redRSaveLoad.saveDocumentAs()

    def menuItemSaveTemplate(self):
        redRSaveLoad.saveTemplate()
    def menuItemSaveAsAppButtons(self):
        return ## depricated
        self.canvas.schema.saveDocumentAsApp(asTabs = 0)

    def menuItemSaveAsAppTabs(self):
        return ## depricated
        self.canvas.schema.saveDocumentAsApp(asTabs = 1)
        
    def menuItemPrinter(self):
        try:
            printer = QPrinter()
            printDialog = QPrintDialog(printer)
            if printDialog.exec_() == QDialog.Rejected: 
                
                return
            painter = QPainter(printer)
            self.canvas.schema.canvas.render(painter)
            painter.end()
            for widget in self.canvas.schema.widgets:
                try:
                    widget.instance.printWidget(printer)                
                except: pass
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, "Error in printing the schema")
        
        self.reports.createReportsMenu(self.canvas.schema.widgets)
        

    def readRecentFiles(self):
        self.menuRecent.clear()
        if not redREnviron.settings.has_key("RecentFiles"): return
        recentDocs = redREnviron.settings["RecentFiles"]

        # remove missing recent files
        for i in range(len(recentDocs)-1,-1,-1):
            if not os.path.exists(recentDocs[i]):
                recentDocs.remove(recentDocs[i])

        recentDocs = recentDocs[:9]
        redREnviron.settings["RecentFiles"] = recentDocs
        #print recentDocs, 'Recent Docs'
        for i in range(len(recentDocs)):
            shortName = "&" + unicode(i+1) + " " + os.path.basename(recentDocs[i])
            self.menuRecent.addAction(shortName, lambda k = i+1: self.openRecentFile(k))
            #print 'Added doc ', shortName, ' to position ', i

    def openRecentFile(self, index):
        if len(redREnviron.settings["RecentFiles"]) >= index:
            self.canvas.schema.clear()
            redRSaveLoad.loadDocument(redREnviron.settings["RecentFiles"][index-1])
            self.addToRecentMenu(redREnviron.settings["RecentFiles"][index-1])

    def addToRecentMenu(self, name):
        recentDocs = []
        if redREnviron.settings.has_key("RecentFiles"):
            recentDocs = redREnviron.settings["RecentFiles"]

        # convert to a valid file name
        name = os.path.realpath(name)

        if name in recentDocs:
            recentDocs.remove(name)
        recentDocs.insert(0, name)

        if len(recentDocs)> 5:
            recentDocs.remove(recentDocs[5])
        redREnviron.settings["RecentFiles"] = recentDocs
        self.readRecentFiles()

    def menuItemSelectAll(self):
        return

    def updateSnapToGrid(self):
        if redREnviron.settings["snapToGrid"]:
            for widget in self.canvas.schema.widgets:
                widget.setCoords(widget.x(), widget.y())
            self.canvas.schema.canvas.update()

    def menuItemEnableAll(self):
        self.canvas.schema.enableAllLines()

    def menuItemDisableAll(self):
        self.canvas.schema.disableAllLines()
    def selectAllWidgets(self):
        self.canvas.schema.selectAllWidgets()
    def menuItemSaveSettings(self):
        self.menuSaveSettings = not self.menuSaveSettings
        self.menuOptions.setItemChecked(self.menuSaveSettingsID, self.menuSaveSettings)

    def menuItemNewScheme(self):
        self.canvas.schema.clear()

    def dumpVariables(self):
        self.canvas.schema.dumpWidgetVariables()

    def menuItemShowOutputWindow(self):
        self.canvas.outputDock.show()
    
    def showOutputException(self):
        self.output.hide()
        self.output.show()
        self.output.showExceptionTab()
    def menuItemReport(self):
        ## start the report generator, handled in orngDoc (where else)
        self.canvas.reports.createReportsMenu()

        
    def menuItemClearOutputWindow(self):
        self.canvas.printOutput.clear()
        
        

    def menuItemSaveOutputWindow(self):
        qname = QFileDialog.getSaveFileName(self.canvas, "Save Output To File", 
        redREnviron.settings['logFile'], "HTML Document (*.html)")
        if qname.isEmpty(): return
        qname = unicode(qname)

        text = unicode(self.canvas.printOutput.toHtml())

        file = open(qname, "wt")
        file.write(text)
        file.close()


    def menuItemShowToolbar(self):
        redREnviron.settings["showToolbar"] = not redREnviron.settings.get("showToolbar", True)
        if redREnviron.settings["showToolbar"]: self.toolbar.show()
        else: self.toolbar.hide()

    def menuItemShowWidgetToolbar(self):
        redREnviron.settings["showWidgetToolbar"] = not redREnviron.settings.get("showWidgetToolbar", True)
        if redREnviron.settings["showWidgetToolbar"]: self.widgetsToolBar.show()
        else: self.widgetsToolBar.hide()


    def menuItemEditWidgetShortcuts(self):
        dlg = orngDlgs.WidgetShortcutDlg(self)
        if dlg.exec_() == QDialog.Accepted:
            self.widgetShortcuts = dict([(y, x) for x, y in dlg.invDict.items()])
            shf = file(os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "shortcuts.txt"), "wt")
            for k, widgetInfo in self.widgetShortcuts.items():
                shf.write("%s: %s\n" % (k, (widgetInfo.packageName, widgetInfo.name)))

    def menuItemDeleteWidgetSettings(self):
        if QMessageBox.warning(self,'Red Canvas','If you want to delete widget settings press Ok, otherwise press Cancel.\nFor the deletion to be complete there cannot be any widgets on your schema.\nIf there are, clear the schema first.',QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape) == QMessageBox.Ok:
            if os.path.exists(redREnviron.directoryNames['widgetSettingsDir']):
                for f in os.listdir(redREnviron.directoryNames['widgetSettingsDir']):
                    if os.path.splitext(f)[1].lower() == ".ini":
                        os.remove(os.path.join(redREnviron.directoryNames['widgetSettingsDir'], f))

    def menuOpenPackageManager(self):
        self.canvas.packageManagerGUI.exec_()
 
    def menuCheckForUpdates(self):
        self.canvas.updateManager.showUpdateDialog(auto=False)
       
    def menuOpenLocalOrangeHelp(self):
        import webbrowser
        webbrowser.open("file:///" + os.path.join(redREnviron.directoryNames['redRDir'], "doc/catalog/index.html"))

    def menuOpenLocalCanvasHelp(self):
        import webbrowser
        webbrowser.open(os.path.join(redREnviron.directoryNames['redRDir'], "doc/canvas/default.htm"))
    def menuItemInstallPackage(self):
        name = QFileDialog.getOpenFileName(self.canvas, "Install Package", 
        redREnviron.settings["saveSchemaDir"], "Package (*.zip)")
        if name.isEmpty(): return
        name = unicode(name)
        redREnviron.settings['saveSchemaDir'] = os.path.split(unicode(name))[0]
        self.packageManagerGUI.show()
        self.packageManagerGUI.installPackageFromFile(unicode(name))

    def menuOpenOnlineOrangeHelp(self):
        import webbrowser
        webbrowser.open("http://www.red-r.org")

    def menuOpenOnlineCanvasHelp(self):
        import webbrowser
        #webbrowser.open("http://www.ailab.si/orange/orangeCanvas") # to be added on the web
        webbrowser.open("http://www.red-r.org")

    # def menuCheckForUpdates(self):
        # import updateOrange
        # self.updateDlg = updateOrange.updateOrangeDlg(None, "", Qt.WDestructiveClose)
        #redREnviron.settings['svnSettings'], redREnviron.settings['versionNumber'] = updateRedR.start(redREnviron.settings['svnSettings'], redREnviron.settings['versionNumber'], silent = False)
        pass
    def menuItemAboutOrange(self):
        dlg = orngDlgs.AboutDlg()
        dlg.exec_()

    def menuItemCanvasOptions(self):
        dlg = orngDlgs.CanvasOptionsDlg(self.canvas, None)
        if dlg.exec_() == QDialog.Accepted:
            if redREnviron.settings["snapToGrid"] != dlg.settings["snapToGrid"]:
                self.updateSnapToGrid()
            self.updateStyle()
            self.canvas.createWidgetsToolbar()

    def updateStyle(self):
        if not redREnviron.settings.has_key("style"):
            lowerItems = [unicode(n).lower() for n in QStyleFactory.keys()]
            currStyle = unicode(qApp.style().objectName()).lower()
            redREnviron.settings.setdefault("style", redRStyle.QtStyles[lowerItems.index(currStyle)])

        QApplication.setStyle(QStyleFactory.create(redREnviron.settings["style"]))

        # we want buttons to go in the "windows" direction (Yes, No, Cancel)
        # qApp.setStyleSheet(" QDialogButtonBox { button-layout: 0; }")       
        
        if redREnviron.settings["useDefaultPalette"]:
            QApplication.setPalette(qApp.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

class SearchBox(redRlineEditHint):
    def __init__(self, widget, label='Search',orientation='horizontal', items = [], toolTip = None,  width = -1, callback = None, **args):
        redRlineEditHint.__init__(self, widget = widget, label = label,displayLabel=True,
        orientation = orientation, items = items, toolTip = toolTip, width = width, callback = self.searchCallback, **args)
        self.searchBox = redRSearchDialog()
        QObject.connect(self, SIGNAL('returnPressed()'), self.searchDialog)
        self.caseSensitive = 0
        self.matchAnywhere = 1
        self.autoSizeListWidget = 1
        
        widgetList = []
        for wName, widgetInfo in redRObjects.widgetRegistry()['widgets'].items():
            x = QListWidgetItem(QIcon(widgetInfo.icon), unicode(wName))
            widgetList.append(x)
            
        self.setItems(widgetList)
            
    def eventFilter(self, object, ev):
        try: # a wrapper that prevents problems for the listbox debigging should remove this
            if object != self.listWidget and object != self:
                return 0
            if ev.type() == QEvent.MouseButtonPress:
                self.listWidget.hide()
                return 1
                    
            consumed = 0
            if ev.type() == QEvent.KeyPress:
                consumed = 1
                if ev.key() in [Qt.Key_Enter, Qt.Key_Return]:
                    # print 'Return pressed'
                    self.doneCompletion()
                elif ev.key() == Qt.Key_Escape:
                    self.listWidget.hide()
                    # self.setFocus()
                elif ev.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown]:
                    
                    self.listWidget.setFocus()
                    self.listWidget.event(ev)
                else:
                    # self.setFocus()
                    self.event(ev)
            return consumed
        except: return 0
        
    def searchDialog(self):
        if unicode(self.text()) in self.itemsAsStrings:
            return
        else:
            itemText = unicode(self.text())
            #print 'Searching '+itemText+' on Red-R.org'
            self.searchBox.show()
            url = 'http://www.red-r.org/?s='+itemText
            self.searchBox.updateUrl(url)
    
    def searchCallback(self):
        
        qApp.canvasDlg.schema.addWidget(redRObjects.widgetRegistry()['widgets'][unicode(self.text())]) # add the correct widget to the schema
        self.clear()  # clear the line edit for the next widget
        return
        #text = unicode(self.widgetSuggestEdit.text())
        
        # if '.rrts' in text: ## this is a template, we should load this and not add the widget
            # for action in self.templateActions:
                # if action.templateInfo.name == text:
                    # redRSaveLoad.loadTemplate(action.templateInfo.file)
                    # return
        # else: ## if there isn't a .rrts in the filename then we should proceed as normal
            # for action in self.actions: # move through all of the actions in the actions list
                # if action.widgetInfo.name == text: # find the widget (action) that has the correct name, note this finds the first instance.  Widget names must be unique   ??? should we allow multiple widgets with the same name ??? probably not.
                    # self.widgetInfo = action.widgetInfo
                    # self.canvas.schema.addWidget(action.widgetInfo) # add the correct widget to the schema
                    
                    # self.widgetSuggestEdit.clear()  # clear the line edit for the next widget
                    # return
    

