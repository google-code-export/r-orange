# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modifications by Kyle R Covington and Anup Parikh
# Description:
#    main file, that creates the MDI environment
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys, os, cPickle
mypath = os.path.split(os.path.split(os.path.abspath(sys.argv[0]))[0])[0]
sys.path.insert(0, mypath)
import redREnviron
import orngRegistry, OWGUI
import orngTabs, orngDoc, orngDlgs, orngOutput, orngHelp, OWReport
# import user


class OrangeCanvasDlg(QMainWindow):
    
    def __init__(self, app, parent = None, flags =  0):
        QMainWindow.__init__(self, parent)
        
        self.version = {}
        self.version = self.getVersion()
        self.debugMode = 0        # print extra output for debuging
        self.setWindowTitle("Red-R Canvas")
        self.windows = []    # list of id for windows in Window menu
        self.recentDocs = []
        self.iconNameToIcon = {}
        self.toolbarIconSizeList = [16, 32, 40, 48, 60]
        self.schemeIconSizeList = [32, 40, 48]
        self.widgetsToolBar = None
        self.originalPalette = QApplication.palette()
        

        self.__dict__.update(redREnviron.directoryNames)
        # print self.tempDir
        # print redREnviron.directoryNames['tempDir']
        logo = QPixmap(os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "splash.png"))
        splashWindow = QSplashScreen(logo, Qt.WindowStaysOnTopHint)
        splashWindow.setMask(logo.mask())
        splashWindow.show()
        splashWindow.showMessage("Settings Icons", Qt.AlignHCenter + Qt.AlignBottom)
        self.defaultPic = os.path.join(self.picsDir, "Unknown.png")
        self.defaultBackground = os.path.join(self.picsDir, "frame.png")
        canvasPicsDir  = os.path.join(self.canvasDir, "icons")
        self.file_new  = os.path.join(canvasPicsDir, "doc.png")
        self.outputPix = os.path.join(canvasPicsDir, "output.png")
        self.file_open = os.path.join(canvasPicsDir, "open.png")
        self.file_save = os.path.join(canvasPicsDir, "save.png")
        self.reload_pic = os.path.join(canvasPicsDir, "update1.png")
        self.showAll_pic = os.path.join(canvasPicsDir, "upgreenarrow.png")
        self.closeAll_pic = os.path.join(canvasPicsDir, "downgreenarrow.png")
        self.text_icon = os.path.join(canvasPicsDir, "text.png")
        self.file_print= os.path.join(canvasPicsDir, "print.png")
        self.file_exit = os.path.join(canvasPicsDir, "exit.png")
        canvasIconName = os.path.join(canvasPicsDir, "CanvasIcon.png")
        if os.path.exists(canvasIconName):
            self.setWindowIcon(QIcon(canvasIconName))
        
        self.settings = {}
        self.settings['CRANrepos'] = 'http://cran.r-project.org'
        
        self.menuSaveSettingsID = -1
        self.menuSaveSettings = 1
        splashWindow.showMessage("Loading Settings", Qt.AlignHCenter + Qt.AlignBottom)
        self.loadSettings()
        
        ## set the temp directory for this session
        if not os.path.exists(os.path.join(self.canvasSettingsDir, 'temp')):
            os.mkdir(os.path.join(self.canvasSettingsDir, 'temp')) ## should only need to be done once.
        
        # print '####################################\n'*10,self.settings

        self.widgetSelectedColor = QColor(*self.settings["widgetSelectedColor"])
        self.widgetActiveColor   = QColor(*self.settings["widgetActiveColor"])
        self.lineColor           = QColor(*self.settings["lineColor"])

        if not self.settings.has_key("WidgetTabs") or self.settings["WidgetTabs"] == []:
            self.settings["WidgetTabs"] = [(name, Qt.Checked) for name in ["Data", "Visualize", "Classify", "Regression", "Evaluate", "Unsupervised", "Associate", "Text", "Genomics", "Prototypes"]]
        
        # output window
        splashWindow.showMessage("Setting Outputs", Qt.AlignHCenter + Qt.AlignBottom)
        self.output = orngOutput.OutputWindow(self)
        self.output.catchException(1)
        self.output.catchOutput(1)

        # create error and warning icons
        splashWindow.showMessage("Setting Icons", Qt.AlignHCenter + Qt.AlignBottom)
        informationIconName = os.path.join(canvasPicsDir, "information.png")
        warningIconName = os.path.join(canvasPicsDir, "warning.png")
        errorIconName = os.path.join(canvasPicsDir, "error.png")
        if os.path.exists(errorIconName) and os.path.exists(warningIconName) and os.path.exists(informationIconName):
            self.errorIcon = QPixmap(errorIconName)
            self.warningIcon = QPixmap(warningIconName)
            self.informationIcon = QPixmap(informationIconName)
            self.widgetIcons = {"Info": self.informationIcon, "Warning": self.warningIcon, "Error": self.errorIcon}
        else:
            self.errorIcon = None
            self.warningIcon = None
            self.informationIcon = None
            self.widgetIcons = None
            print "Unable to load all necessary icons. Please reinstall Red-R."

        self.setStatusBar(MyStatusBar(self))
                
        self.widgetRegistry = orngRegistry.readCategories() # the widget registry has been created
        
        # print self.widgetRegistry
        self.updateStyle()
        
        # create toolbar
        splashWindow.showMessage("Creating Toolbar", Qt.AlignHCenter + Qt.AlignBottom)
        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.setOrientation(Qt.Horizontal)
        if not self.settings.get("showToolbar", True): self.toolbar.hide()
        
        # create a schema
        self.schema = orngDoc.SchemaDoc(self)
        
        self.setCentralWidget(self.schema)
        self.schema.setFocus()

        

        # create menu
        splashWindow.showMessage("Creating Menu", Qt.AlignHCenter + Qt.AlignBottom)
        self.initMenu()

        self.toolbar.addAction(QIcon(self.file_open), "Open schema", self.menuItemOpen)
        self.toolSave = self.toolbar.addAction(QIcon(self.file_save), "Save schema", self.menuItemSave)
        self.toolReloadWidgets = self.toolbar.addAction(QIcon(self.reload_pic), "Reload Widgets", self.reloadWidgets)
        self.toolbar.addAction(QIcon(self.showAll_pic), "Show All Widget Windows", self.schema.showAllWidgets)
        self.toolbar.addAction(QIcon(self.closeAll_pic), "Close All Widget Windows", self.schema.closeAllWidgets)
        self.toolbar.addSeparator()
        self.toolbar.addAction(QIcon(self.file_print), "Print", self.menuItemPrinter)

        self.toolbar.addSeparator()

        w = QWidget()
        w.setLayout(QHBoxLayout())
        items = ["%d x %d" % (v,v) for v in self.toolbarIconSizeList]
        self.settings["toolbarIconSize"] = min(len(items)-1, self.settings["toolbarIconSize"])
        OWGUI.comboBoxWithCaption(w, self.settings, "toolbarIconSize", "Icon size:", items = items, tooltip = "Set the size of the widget icons in the toolbar, tool box, and tree view area", callback = self.createWidgetsToolbar, debuggingEnabled = 0)
        self.toolbar.addWidget(w)
        
        self.addToolBarBreak()
        self.createWidgetsToolbar() # also creates the categories popup
        
        
        self.readShortcuts()
        self.readRecentFiles()

        
        splashWindow.showMessage("Setting States", Qt.AlignHCenter + Qt.AlignBottom)
        if 'windowState' in self.settings.keys():
            self.restoreState(self.settings['windowState'])
        if 'geometry' in self.settings.keys():
            self.restoreGeometry(self.settings['geometry'])
       
        if 'size' in self.settings.keys():
            self.resize(self.settings['size'])
        else:
        # center window in the desktop
        # in newer versions of Qt we can also find the center of a primary screen
        # on multiheaded desktops
            
            width, height = self.settings.get("canvasWidth", 700), self.settings.get("canvasHeight", 600)
            desktop = app.desktop()
            deskH = desktop.screenGeometry(desktop.primaryScreen()).height()
            deskW = desktop.screenGeometry(desktop.primaryScreen()).width()
            h = max(0, deskH/2 - height/2)  # if the window is too small, resize the window to desktop size
            w = max(0, deskW/2 - width/2)
            self.move(w,h+2)
            self.resize(width,height)
        if 'pos' in self.settings.keys():
            self.move(self.settings['pos'])


        # self.helpWindow = orngHelp.HelpWindow(self)
        # self.reportWindow = OWReport.ReportWindow()
        
        self.show()

        # did Orange crash the last time we used it? If yes, you will find a temSchema.tmp file
        # if os.path.exists(os.path.join(self.canvasSettingsDir, "tempSchema.tmp")):
            # mb = QMessageBox('RedR Canvas', "Your previous RedR Canvas session was not closed successfully.\nYou can choose to reload your unsaved work or start a new session.\n\nIf you choose 'Reload', the links will be disabled to prevent reoccurence of the crash.\nYou can enable them by clicking Options/Enable all links.", QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape, QMessageBox.NoButton)
            # mb.setButtonText(QMessageBox.Ok, "Reload")
            # mb.setButtonText(QMessageBox.Cancel, "New schema")
            # if mb.exec_() == QMessageBox.Ok:
                # self.schema.loadDocument(os.path.join(self.canvasSettingsDir, "tempSchema.tmp"), freeze = 1)
        
        
        
        
        # show message box if no numpy
        # splashWindow.showMessage("Processing Events", Qt.AlignHCenter + Qt.AlignBottom)
        if splashWindow:
            splashWindow.hide()

        qApp.processEvents()
        try:
            import numpy
        except:
            if QMessageBox.warning(self,'Red Canvas','Several widgets now use numpy module, \nthat is not yet installed on this computer. \nDo you wish to download it?',QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape) == QMessageBox.Ok:
                import webbrowser
                webbrowser.open("http://sourceforge.net/projects/numpy/")
        
        

        
    def createWidgetsToolbar(self):
        orngTabs.constructCategoriesPopup(self)
        float = False
        if self.widgetsToolBar:
            if self.widgetsToolBar.isFloating():
                float = True

            self.settings["showWidgetToolbar"] = self.widgetsToolBar.isVisible()
            self.settings["toolboxWidth"] = self.widgetsToolBar.treeWidget.width()
            self.removeDockWidget(self.widgetsToolBar)

            
        self.tabs = self.widgetsToolBar = orngTabs.WidgetTree(self, self.widgetRegistry)
        self.widgetsToolBar.setWindowTitle('Widget Toolbar')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.widgetsToolBar)
        self.widgetsToolBar.setFloating(float)

        self.settings["WidgetTabs"] = self.tabs.createWidgetTabs(self.settings["WidgetTabs"], self.widgetRegistry, self.widgetDir, self.picsDir, self.defaultPic)
        self.widgetsToolBar.treeWidget.collapseAll()
        
    def getVersion(self):
        if len(self.version.keys()) ==0:
            f = open(os.path.join(redREnviron.directoryNames["redRDir"],'version.txt'), 'r')
            file = f.readlines()
            f.close()
            import re
            for i in file:
                m = re.search('!define\s(\S+)\s"(.*)"',i)
                self.version[m.group(1)] = m.group(2)
        return self.version

    def readShortcuts(self):
        self.widgetShortcuts = {}
        shfn = os.path.join(self.canvasSettingsDir, "shortcuts.txt")
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


    def initMenu(self):
        self.menuRecent = QMenu("Recent Schemas", self)

        self.menuFile = QMenu("&File", self)
        self.menuFile.addAction( "New Scheme",  self.menuItemNewScheme, QKeySequence.New)
        self.menuFile.addAction(QIcon(self.file_open), "&Open...", self.menuItemOpen, QKeySequence.Open )
        self.menuFile.addAction(QIcon(self.file_open), "&Open and Freeze...", self.menuItemOpenFreeze)
        self.menuFile.addAction("Import Schema", self.importSchema)
        if os.path.exists(os.path.join(self.canvasSettingsDir, "lastSchema.tmp")):
            self.menuFile.addAction("Reload Last Schema", self.menuItemOpenLastSchema, Qt.CTRL+Qt.Key_R)
        #self.menuFile.addAction( "&Clear", self.menuItemClear)
        self.menuFile.addSeparator()
        self.menuSaveID = self.menuFile.addAction(QIcon(self.file_save), "&Save", self.menuItemSave, QKeySequence.Save )
        self.menuSaveAsID = self.menuFile.addAction( "Save &As...", self.menuItemSaveAs)
        self.menuSaveTemplateID = self.menuFile.addAction( "Save As Template", self.menuItemSaveTemplate)
        #self.menuFile.addAction( "&Save as Application (Tabs)...", self.menuItemSaveAsAppTabs)
        #self.menuFile.addAction( "&Save as Application (Buttons)...", self.menuItemSaveAsAppButtons)
        self.menuFile.addSeparator()
        self.menuFile.addAction(QIcon(self.file_print), "&Print Schema / Save image", self.menuItemPrinter, QKeySequence.Print )
        self.menuFile.addSeparator()
        self.menuFile.addMenu(self.menuRecent)
        self.menuFile.addSeparator()
        self.menuFile.addAction( "E&xit",  self.close, Qt.CTRL+Qt.Key_Q )

        self.menuOptions = QMenu("&Options", self)
        self.menuOptions.addAction( "Enable All Links",  self.menuItemEnableAll, Qt.CTRL+Qt.Key_E)
        self.menuOptions.addAction( "Disable All Links",  self.menuItemDisableAll, Qt.CTRL+Qt.Key_D)
        self.menuOptions.addSeparator()
        self.menuOptions.addAction("Show Output Window", self.menuItemShowOutputWindow)
        self.menuOptions.addAction("Clear Output Window", self.menuItemClearOutputWindow)
        self.menuOptions.addAction("Save Output Text...", self.menuItemSaveOutputWindow)

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

        localHelp = 0
        self.menuHelp = QMenu("&Help", self)
        if os.path.exists(os.path.join(self.redRDir, r"doc/reference/default.htm")) or os.path.exists(os.path.join(self.redRDir, r"doc/canvas/default.htm")):
            if os.path.exists(os.path.join(self.redRDir, r"doc/reference/default.htm")): self.menuHelp.addAction("Red-R Help", self.menuOpenLocalOrangeHelp)
            if os.path.exists(os.path.join(self.redRDir, r"doc/canvas/default.htm")): self.menuHelp.addAction("Red Canvas Help", self.menuOpenLocalCanvasHelp)

        self.menuHelp.addAction("Red-R Online Help", self.menuOpenOnlineOrangeHelp)
        #self.menuHelp.addAction("Orange Canvas Online Help", self.menuOpenOnlineCanvasHelp)

        if os.path.exists(os.path.join(self.redRDir, r"updateOrange.py")):
            self.menuHelp.addSeparator()
            self.menuHelp.addAction("Check for updates", self.menuCheckForUpdates)
            
        self.menuHelp.addSeparator()
        self.menuHelp.addAction("About Red-R", self.menuItemAboutOrange)

        # widget popup menu
        self.widgetPopup = QMenu("Widget", self)
        self.widgetPopup.addAction( "Open",  self.schema.canvasView.openActiveWidget)
        self.widgetPopup.addSeparator()
        rename = self.widgetPopup.addAction( "&Rename", self.schema.canvasView.renameActiveWidget, Qt.Key_F2)
        delete = self.widgetPopup.addAction("Remove", self.schema.canvasView.removeActiveWidget, Qt.Key_Delete)
        self.widgetPopup.setEnabled(0)

        self.menuBar = QMenuBar(self)
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuOptions)
        self.menuBar.addMenu(self.widgetPopup)
        self.menuBar.addMenu(self.menuHelp)
        self.setMenuBar(self.menuBar)
    def importSchema(self):
        name = QFileDialog.getOpenFileName(self, "Import File", self.settings["saveSchemaDir"], "Red-R Widget Schema (*.rrs *.rrts)")
        if name.isEmpty(): return
        
        self.settings['saveSchemaDir'] = os.path.split(str(name))[0]
        self.schema.loadDocument(str(name), freeze = 0, importing = True)
        self.addToRecentMenu(str(name))
        
    def menuItemOpen(self):
        name = QFileDialog.getOpenFileName(self, "Open File", 
        self.settings["saveSchemaDir"], "Schema or Template (*.rrs *.rrts)")
        if name.isEmpty(): return
        
        self.settings['saveSchemaDir'] = os.path.split(str(name))[0]
        self.schema.clear()
        self.schema.loadDocument(str(name), freeze = 0, importing = False)
        self.addToRecentMenu(str(name))

    def menuItemOpenFreeze(self):
        name = QFileDialog.getOpenFileName(self, "Open File", 
        self.settings["saveSchemaDir"], "Schema or Template (*.rrs *.rrts)")
        if name.isEmpty():
            return
        self.schema.clear()
        self.schema.loadDocument(str(name), freeze = 1)
        self.addToRecentMenu(str(name))

    def menuItemOpenLastSchema(self):
        fullName = os.path.join(self.canvasSettingsDir, "lastSchema.tmp")
        if os.path.exists(fullName):
            self.schema.loadDocument(fullName)

    def menuItemSave(self):
        print 'click save'
        self.schema.saveDocument()
    def reloadWidgets(self): # should have a way to set the desired tab location 
        self.widgetRegistry = orngRegistry.readCategories()
        #import redRGUI
        self.createWidgetsToolbar()
        #self.widgetsToolBar.show()
    def menuItemSaveAs(self):
        self.schema.saveDocumentAs()

    def menuItemSaveTemplate(self):
        self.schema.saveTemplate()
    def menuItemSaveAsAppButtons(self):
        self.schema.saveDocumentAsApp(asTabs = 0)

    def menuItemSaveAsAppTabs(self):
        self.schema.saveDocumentAsApp(asTabs = 1)

    def menuItemPrinter(self):
        try:
            printer = QPrinter()
            printDialog = QPrintDialog(printer)
            if printDialog.exec_() == QDialog.Rejected: 
                print 'Printing Rejected'
                return
            painter = QPainter(printer)
            self.schema.canvas.render(painter)
            painter.end()
            for widget in self.schema.widgets:
                try:
                    widget.instance.printWidget(printer)                
                except: pass
        except:
            print "Error in printing the schema"
        

    def readRecentFiles(self):
        self.menuRecent.clear()
        if not self.settings.has_key("RecentFiles"): return
        recentDocs = self.settings["RecentFiles"]

        # remove missing recent files
        for i in range(len(recentDocs)-1,-1,-1):
            if not os.path.exists(recentDocs[i]):
                recentDocs.remove(recentDocs[i])

        recentDocs = recentDocs[:9]
        self.settings["RecentFiles"] = recentDocs
        #print recentDocs, 'Recent Docs'
        for i in range(len(recentDocs)):
            shortName = "&" + str(i+1) + " " + os.path.basename(recentDocs[i])
            self.menuRecent.addAction(shortName, lambda k = i+1: self.openRecentFile(k))
            #print 'Added doc ', shortName, ' to position ', i

    def openRecentFile(self, index):
        if len(self.settings["RecentFiles"]) >= index:
            self.schema.clear()
            self.schema.loadDocument(self.settings["RecentFiles"][index-1])
            self.addToRecentMenu(self.settings["RecentFiles"][index-1])

    def addToRecentMenu(self, name):
        recentDocs = []
        if self.settings.has_key("RecentFiles"):
            recentDocs = self.settings["RecentFiles"]

        # convert to a valid file name
        name = os.path.realpath(name)

        if name in recentDocs:
            recentDocs.remove(name)
        recentDocs.insert(0, name)

        if len(recentDocs)> 5:
            recentDocs.remove(recentDocs[5])
        self.settings["RecentFiles"] = recentDocs
        self.readRecentFiles()

    def menuItemSelectAll(self):
        return

    def updateSnapToGrid(self):
        if self.settings["snapToGrid"]:
            for widget in self.schema.widgets:
                widget.setCoords(widget.x(), widget.y())
            self.schema.canvas.update()

    def menuItemEnableAll(self):
        self.schema.enableAllLines()

    def menuItemDisableAll(self):
        self.schema.disableAllLines()

    def menuItemSaveSettings(self):
        self.menuSaveSettings = not self.menuSaveSettings
        self.menuOptions.setItemChecked(self.menuSaveSettingsID, self.menuSaveSettings)

    def menuItemNewScheme(self):
        self.schema.clear()

    def dumpVariables(self):
        self.schema.dumpWidgetVariables()

    def menuItemShowOutputWindow(self):
        self.output.hide()
        self.output.show()
        #self.output.setFocus()

    def menuItemClearOutputWindow(self):
        self.output.textOutput.clear()
        self.statusBar().showMessage("")

    def menuItemSaveOutputWindow(self):
        qname = QFileDialog.getSaveFileName(self, "Save Output To File", self.canvasSettingsDir + "/Output.html", "HTML Document (*.html)")
        if qname.isEmpty(): return
        name = str(qname)

        text = str(self.output.textOutput.toHtml())
        #text = text.replace("</nobr>", "</nobr><br>")

        file = open(name, "wt")
        file.write(text)
        file.close()


    def menuItemShowToolbar(self):
        self.settings["showToolbar"] = not self.settings.get("showToolbar", True)
        if self.settings["showToolbar"]: self.toolbar.show()
        else: self.toolbar.hide()

    def menuItemShowWidgetToolbar(self):
        self.settings["showWidgetToolbar"] = not self.settings.get("showWidgetToolbar", True)
        if self.settings["showWidgetToolbar"]: self.widgetsToolBar.show()
        else: self.widgetsToolBar.hide()


    def menuItemEditWidgetShortcuts(self):
        dlg = orngDlgs.WidgetShortcutDlg(self)
        if dlg.exec_() == QDialog.Accepted:
            self.widgetShortcuts = dict([(y, x) for x, y in dlg.invDict.items()])
            shf = file(os.path.join(self.canvasSettingsDir, "shortcuts.txt"), "wt")
            for k, widgetInfo in self.widgetShortcuts.items():
                shf.write("%s: %s\n" % (k, (widgetInfo.category, widgetInfo.name)))

    def menuItemDeleteWidgetSettings(self):
        if QMessageBox.warning(self,'Red Canvas','If you want to delete widget settings press Ok, otherwise press Cancel.\nFor the deletion to be complete there cannot be any widgets on your schema.\nIf there are, clear the schema first.',QMessageBox.Ok | QMessageBox.Default, QMessageBox.Cancel | QMessageBox.Escape) == QMessageBox.Ok:
            if os.path.exists(self.widgetSettingsDir):
                for f in os.listdir(self.widgetSettingsDir):
                    if os.path.splitext(f)[1].lower() == ".ini":
                        os.remove(os.path.join(self.widgetSettingsDir, f))

    def menuOpenLocalOrangeHelp(self):
        import webbrowser
        webbrowser.open("file:///" + os.path.join(self.redRDir, "doc/catalog/index.html"))

    def menuOpenLocalCanvasHelp(self):
        import webbrowser
        webbrowser.open(os.path.join(self.redRDir, "doc/canvas/default.htm"))

    def menuOpenOnlineOrangeHelp(self):
        import webbrowser
        webbrowser.open("http://www.red-r.org")

    def menuOpenOnlineCanvasHelp(self):
        import webbrowser
        #webbrowser.open("http://www.ailab.si/orange/orangeCanvas") # to be added on the web
        webbrowser.open("http://www.red-r.org")

    def menuCheckForUpdates(self):
        # import updateOrange
        # self.updateDlg = updateOrange.updateOrangeDlg(None, "", Qt.WDestructiveClose)
        #self.settings['svnSettings'], self.settings['versionNumber'] = updateRedR.start(self.settings['svnSettings'], self.settings['versionNumber'], silent = False)
        pass
    def menuItemAboutOrange(self):
        dlg = orngDlgs.AboutDlg()
        dlg.exec_()




    def menuItemCanvasOptions(self):
        dlg = orngDlgs.CanvasOptionsDlg(self, None)

        if dlg.exec_() == QDialog.Accepted:
            if self.settings["snapToGrid"] != dlg.settings["snapToGrid"]:
                self.updateSnapToGrid()

            self.settings.update(dlg.settings)
            self.updateStyle()
            
            self.widgetSelectedColor = dlg.selectedWidgetIcon.color
            self.widgetActiveColor   = dlg.activeWidgetIcon.color
            self.lineColor           = dlg.lineIcon.color
            
            # update settings in widgets in current documents
            for widget in self.schema.widgets:
                widget.instance._useContexts = self.settings["useContexts"]
                widget.instance._owInfo      = self.settings["owInfo"]
                widget.instance._owWarning   = self.settings["owWarning"]
                widget.instance._owError     = self.settings["owError"]
                widget.instance._owShowStatus= self.settings["owShow"]
                # widget.instance.updateStatusBarState()
                widget.resetWidgetSize()
                widget.updateWidgetState()
                
            # update tooltips for lines in all documents
            for line in self.schema.lines:
                line.showSignalNames = self.settings["showSignalNames"]
                line.updateTooltip()
            
            self.schema.canvasView.repaint()
        
            import redREnviron, orngRegistry
            if dlg.toAdd != []:
                for (name, dir) in dlg.toAdd: 
                    redREnviron.registerAddOn(name, dir)
            
            if dlg.toRemove != []:
                for (name, dir) in dlg.toRemove:
                    redREnviron.registerAddOn(name, dir, add = False)
            
            if dlg.toAdd != [] or dlg.toRemove != []:
                self.widgetRegistry = orngRegistry.readCategories()


    def updateStyle(self):
        QApplication.setStyle(QStyleFactory.create(self.settings["style"]))
        #QApplication.setStyle(QStyle.QWindowsStyle)
        qApp.setStyleSheet(" QDialogButtonBox { button-layout: 0; }")       # we want buttons to go in the "windows" direction (Yes, No, Cancel)
        if self.settings["useDefaultPalette"]:
            QApplication.setPalette(qApp.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)


    def setStatusBarEvent(self, text):
        
        if text == "" or text == None:
            self.statusBar().showMessage("")
            return
        elif text == "\n": return
        text = str(text)
        text = text.replace("<nobr>", ""); text = text.replace("</nobr>", "")
        text = text.replace("<b>", ""); text = text.replace("</b>", "")
        text = text.replace("<i>", ""); text = text.replace("</i>", "")
        text = text.replace("<br>", ""); text = text.replace("&nbsp", "")
        self.statusBar().showMessage("Last event: " + str(text), 5000)

    # Loads settings from the widget's .ini file
    def loadSettings(self):
        filename = os.path.join(self.canvasSettingsDir, "orngCanvas.ini")
        self.settings = {}
        if os.path.exists(filename):
            try:
                self.settings = cPickle.load(open(filename, "rb"))
            except:
                pass

        self.settings.setdefault("widgetListType", 3)
        self.settings.setdefault("iconSize", "40 x 40")
        self.settings.setdefault("toolbarIconSize", 2)
        self.settings.setdefault("toolboxWidth", 200)
        self.settings.setdefault('schemeIconSize', 1)
        self.settings.setdefault("snapToGrid", 1)
        self.settings.setdefault("writeLogFile", 1)
        self.settings.setdefault("dontAskBeforeClose", 0)
        self.settings.setdefault("debugMode", 0)
        self.settings.setdefault("uploadError", 0)
        self.settings.setdefault("askToUploadError", 0)
        #self.settings.setdefault("autoSaveSchemasOnClose", 0)
        self.settings.setdefault("saveWidgetsPosition", 1)
        self.settings.setdefault("svnSettings", None)
        #self.settings.setdefault("versionNumber", 'Version0')
##        self.settings.setdefault("autoLoadSchemasOnStart", 0)
        self.settings.setdefault("CRANrepos", 'http://cran.r-project.org')
        self.settings.setdefault("widgetSelectedColor", (0, 255, 0))
        self.settings.setdefault("widgetActiveColor", (0,0,255))
        self.settings.setdefault("lineColor", (0,255,0))

        #if not self.settings.has_key("catchException"): self.settings["catchException"] = 1
        #if not self.settings.has_key("catchOutput"): self.settings["catchOutput"] = 1

        self.settings.setdefault("saveSchemaDir", self.canvasSettingsDir)
        self.settings.setdefault("saveApplicationDir", self.canvasSettingsDir)
        self.settings.setdefault("showSignalNames", 1)
        self.settings.setdefault("useContexts", 1)

        self.settings.setdefault("canvasWidth", 700)
        self.settings.setdefault("canvasHeight", 600)

        if not self.settings.has_key("style"):
            items = [str(n) for n in QStyleFactory.keys()]
            lowerItems = [str(n).lower() for n in QStyleFactory.keys()]
            currStyle = str(qApp.style().objectName()).lower()
            self.settings.setdefault("style", items[lowerItems.index(currStyle)])
        self.settings.setdefault("useDefaultPalette", 0)

        self.settings.setdefault("focusOnCatchException", 1)
        self.settings.setdefault("focusOnCatchOutput" , 0)
        self.settings.setdefault("printOutputInStatusBar", 1)
        self.settings.setdefault("printExceptionInStatusBar", 1)
        self.settings.setdefault("outputVerbosity", 0)
        self.settings.setdefault("ocShow", 1)
        self.settings.setdefault("owShow", 0)
        self.settings.setdefault("ocInfo", 1)
        self.settings.setdefault("owInfo", 1)
        self.settings.setdefault("ocWarning", 1)
        self.settings.setdefault("owWarning", 1)
        self.settings.setdefault("ocError", 1)
        self.settings.setdefault("owError", 1)
        
        self.settings.setdefault("synchronizeHelp", 1)


    # Saves settings to this widget's .ini file
    def saveSettings(self):
        print 'red-r canvas saveSettings'
        filename = os.path.join(self.canvasSettingsDir, "orngCanvas.ini")
        file=open(filename, "wb")
        if self.settings["widgetListType"] == 1:        # tree view
            self.settings["treeItemsOpenness"] = dict([(key, self.tabs.tabDict[key].isExpanded()) for key in self.tabs.tabDict.keys()])
        cPickle.dump(self.settings, file)
        file.close()

    def closeEvent(self, ce):
        print '|#| redRCanvas closeEvent'
        # save the current width of the toolbox, if we are using it
        if isinstance(self.widgetsToolBar, orngTabs.WidgetToolBox):
            self.settings["toolboxWidth"] = self.widgetsToolBar.toolbox.width()
        self.settings["showWidgetToolbar"] = self.widgetsToolBar.isVisible()
        self.settings["showToolbar"] = self.toolbar.isVisible()
        
        self.settings["geometry"] = self.saveGeometry()
        self.settings["windowState"] = self.saveState()
        self.settings['pos'] = self.pos()
        self.settings['size'] = self.size()
        self.saveSettings()
        # closed = self.schema.close()
        if self.settings['dontAskBeforeClose']:
            res = QMessageBox.No
        else:
            res = QMessageBox.question(self, 'Red-R Canvas','Do you wish to save the schema?', QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
        
        if res == QMessageBox.Yes:
            self.RVariableRemoveSupress = 1
            saveComplete = self.schema.saveDocument()
            closed=True
        elif res == QMessageBox.No:
            closed=True
        else:
            closed=False

        
        if closed:
            self.canvasIsClosing = 1        # output window (and possibly report window also) will check this variable before it will close the window
            import shutil
            shutil.rmtree(redREnviron.directoryNames['tempDir'], True) # remove the tempdir, better hope we saved everything we wanted.
            #self.schema.clear(close = True)  # clear all of the widgets (this closes them) and also close the R session, this is better than just leaving it for garbage collection especially if there are R things still open like plots and the like.
            import RSession
            RSession.Rcommand('quit("no")') # close the entire session dropping anything that was open in case it was left by something else, makes the closing much cleaner than just loosing the session.
            self.output.logFile.close()
            self.output.hide()
            
            ce.accept()
            QMainWindow.closeEvent(self,ce)
        else:
            ce.ignore()
        


    def setCaption(self, caption = ""):
        if caption:
            caption = caption.split(".")[0]
            self.setWindowTitle(caption + " - Red Canvas")
        else:
            self.setWindowTitle("Red Canvas")
    
    def getWidgetIcon(self, widgetInfo):
        if self.iconNameToIcon.has_key(widgetInfo.icon):
            return self.iconNameToIcon[widgetInfo.icon]
        
        iconNames = self.getFullWidgetIconName(widgetInfo)
        iconBackgrounds = self.getFullIconBackgroundName(widgetInfo)
        icon = QIcon()
        if len(iconNames) == 1:
            iconSize = QPixmap(iconNames[0]).width()
            iconBackgrounds = [name for name in iconBackgrounds if QPixmap(name).width() == iconSize]
        for name, back in zip(iconNames, iconBackgrounds):
            image = QPixmap(back).toImage()
            painter = QPainter(image)
            painter.drawPixmap(0, 0, QPixmap(name))
            painter.end()
            icon.addPixmap(QPixmap.fromImage(image))
        self.iconNameToIcon[widgetInfo.icon] = icon
        return icon
            
    
    def getFullWidgetIconName(self, widgetInfo):
        iconName = widgetInfo.icon
        names = []
        name, ext = os.path.splitext(iconName)
        for num in [16, 32, 40, 48, 60]:
            names.append("%s_%d%s" % (name, num, ext))
            
        #widgetDir = str(self.widgetRegistry[widgetInfo.category].directory)  #os.path.split(self.getFileName())[0]
        widgetDir = os.path.join(redREnviron.widgetDir,widgetInfo.package)  #os.path.split(self.getFileName())[0]
        #print widgetDir + '\n' *10
        fullPaths = []
        for paths in [(self.widgetDir, widgetInfo.category), (self.widgetDir,), (self.picsDir,), tuple(), (widgetDir,), (widgetDir, "icons")]:
            for name in names + [iconName]:
                fname = os.path.join(*paths + (name,))
                if os.path.exists(fname):
                    fullPaths.append(fname)
            if len(fullPaths) > 1 and fullPaths[-1].endswith(iconName):
                fullPaths.pop()     # if we have the new icons we can remove the default icon
            if fullPaths != []:
                return fullPaths    
        return [self.defaultPic]
    
    def getFullIconBackgroundName(self, widgetInfo):
        #widgetDir = str(self.widgetRegistry[widgetInfo.category].directory)
        widgetDir = os.path.join(redREnviron.widgetDir,widgetInfo.package)  #os.path.split(self.getFileName())[0]

        fullPaths = []
        for paths in [(widgetDir, "icons"), (redREnviron.widgetDir, "base", "icons"), (self.widgetDir, "icons"), (self.picsDir,), tuple(), (widgetDir,), (widgetDir, "icons")]:
            for name in ["background_%d.png" % num for num in [16, 32, 40, 48, 60]]:
                fname = os.path.join(*paths + (name,))
                # print fname
                if os.path.exists(fname):
                    fullPaths.append(fname)
            if fullPaths != []:
                return fullPaths    
        return [self.defaultBackground]
    
    
class MyStatusBar(QStatusBar):
    def __init__(self, parent):
        QStatusBar.__init__(self, parent)
        self.parentWidget = parent

    def mouseDoubleClickEvent(self, ev):
        self.parentWidget.menuItemShowOutputWindow()
        
        
class OrangeQApplication(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)

        
        
#####################Forked verions of R##############################
# import sys, os, redREnviron, numpy
# if sys.platform=="win32":
    # from rpy_options import set_options
    # set_options(RHOME=redREnviron.directoryNames['RDir'])
# else: # need this because linux doesn't need to use the RPATH
    # print 'Cant find windows environ varuable RPATH, you are not using a win32 machine.'

    
# import rpy
# from multiprocessing.managers import BaseManager
# from multiprocessing import freeze_support
# import Queue


# class Rclass():
    # def R(self, query):
        # try:
            # out = rpy.r(query)  
            # return out
        # except rpy.RPyRException as inst:
            # print inst
            # raise Exception('R Error', str(inst)) 


# class MyManager(BaseManager):
    # pass

#####################Forked verions of R##############################

def main(argv = None):
    if argv == None:
        argv = sys.argv
#####################Forked verions of R##############################
    # qApp.rpy = rpy
    # MyManager.register('Rclass', Rclass)
    # manager = MyManager(address=('localhost', 5000), authkey='abracadabra')
    # manager.start()
    # qApp.R = manager.Rclass()
#####################Forked verions of R##############################
    app = OrangeQApplication(sys.argv)
    QCoreApplication.setOrganizationName("Red-r");
    QCoreApplication.setOrganizationDomain("red-r.com");
    QCoreApplication.setApplicationName("Red-r");

    dlg = OrangeCanvasDlg(app)
    qApp.canvasDlg = dlg
    dlg.show()
    # do we need to load a schema, this happens if you open a saved session.
    if os.path.exists(sys.argv[-1]) and os.path.splitext(sys.argv[-1])[1].lower() == ".rrs": 
        dlg.schema.loadDocument(sys.argv[-1])

    # for arg in sys.argv[1:]:
        # if arg == "-reload":
            # dlg.menuItemOpenLastSchema()
    app.exec_()
    # manager.shutdown()
    # dlg.saveSettings()
    app.closeAllWindows()

if __name__ == "__main__":
    # freeze_support()
    sys.exit(main())
