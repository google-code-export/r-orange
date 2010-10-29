## <redRObjects Module.  This module (not a class) will contain and provide access to widget icons, lines, widget instances, and other redRObjects.  Accessor functions are provided to retrieve these objects, create new objects, and distroy objects.>
    # Copyright (C) 2010 Kyle R Covington

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import orngCanvasItems, redREnviron, orngView, time, orngRegistry

defaultTabName = 'General'
_widgetRegistry = {}
_lines = {}
_widgetIcons = {}
_widgetInstances = {}
_canvasTabs = {}
_canvasView = {}
_canvasScene = {}
_activeTab = ''

def readCategories():
    global _widgetRegistry
    _widgetRegistry = orngRegistry.readCategories()

def widgetRegistry():
    global _widgetRegistry
    if _widgetRegistry == {} or len(_widgetRegistry.keys()) == 0:
        readCategories()
    return _widgetRegistry
    
##############################
######      Tabs        ######
##############################
def tabNames():
    return _canvasView.keys()

def makeTabView(tabname, parent):
    global _activeTab
    w = QWidget()
    w.setLayout(QVBoxLayout())
    _canvasScene[tabname] = QGraphicsScene()
    _canvasView[tabname] = orngView.SchemaView(parent, _canvasScene[tabname], w)
    w.layout().addWidget(_canvasView[tabname])
    _activeTab = tabname
    return w
    
# def removeTabView(tabname, parent):
    
def activeTab():
    global _activeTab
    global _canvasView
    return _canvasView[_activeTab]

def scenes():
    global _canvasScene
    return [s for k, s in _canvasScene.items()]
    
def activeCanvas():
    global _canvasScene
    global _activeTab
    return _canvasScene[_activeTab]
def activeTabName():
    global _activeTab
    return _activeTab
    
def makeSchemaTab(tabname):
    if tabname in _canvasTabs.keys():
        return activeTab(tabname)
        
    _canvasTabs[tabname] = QWidget()
    _canvasTabs[tabname].setLayout(QVBoxLayout())
    _tabsWidget.addTab(_canvasTabs[tabname], tabname)
    #_canvas[tabname] = QGraphicsScene()
    _canvasView[tabname] = orngView.SchemaView(self, _canvas[tabname], _canvasTabs[tabname])
    _canvasTabs[tabname].layout().addWidget(self.canvasView[tabname])
    setActiveTab(tabname)
def setActiveTab(tabname):
    global _activeTab
    _activeTab = tabname
def removeSchemaTab(tabname):
    if tabname == defaultTabName: return ## can't remove the general tab
    global _canvasView
    #global _canvas
    #global _canvasTabs
    global _canvasScene
    del _canvasView[tabname]
    del _canvasScene[tabname]
    #del _canvas[tabname]
    #del _canvasTabs[tabname]
    
    
###############################
#######     icons       #######
###############################
def getIconsByTab(tabs = None):  # returns a dict of lists of icons for a specified tab, if no tab specified then all incons on all tabs are returned.
    global _widgetIcons
    global _canvasScene
    if tabs == None:
        tabs = _canvasScene.keys()
    if type(tabs) != list:
        tabs = [tabs]
    #print tabs, 'Tabs'
    tabIconsList = {}
    for t in tabs:
        #print t
        icons = []
        for k, wi in _widgetIcons.items():
            #print wi
            if wi.tab == t:
                icons.append(wi)
        tabIconsList[t] = icons
    return tabIconsList

def getWidgetByInstance(instance):
    global _widgetIcons
    for k, widget in _widgetIcons.items():
        if widget.instance() == instance:
            return widget
    return None
    
def newIcon(sm, canvas, tab, info, pic, dlg, instanceID, tabName):
    newwidget = orngCanvasItems.CanvasWidget(sm, canvas, tab, info, pic, dlg, instanceID = instanceID, tabName = tabName)
    _widgetIcons[str(time.time())] = newwidget # put a new widget into the stack with a timestamp.
    return newwidget
    
def getIconIDByIcon(icon):
    for k, i in _widgetIcons.items():
        if i == icon:
            return k
    return None

def getIconByIconID(id):
    return _widgetIcons[id]
    
def getIconByIconCaption(caption):
    icons = []
    for k, i in _widgetIcons.items():
        if i.caption == caption:
            icons.append(i)
    return icons
    
def getIconByIconInstanceRef(instance):
    icons = []
    for k, i in _widgetIcons.items():
        if i.instanceID == instance.widgetID:
            icons.append(i)
    return icons
    
def getIconByIconInstanceID(id):
    icons = []
    for k, i in _widgetIcons.items():
        if i.instanceID == id:
            icons.append(i)
    return icons
    
def getWidgetByIDActiveTabOnly(widgetID):
    for k, widget in _widgetIcons.items():
        print widget.instanceID
        if (widget.instanceID == widgetID) and (widget.tab == activeTabName()):
            return widget
    return None
    
def removeWidgetIcon(icon):
    global _widgetIcons
    for k, i in _widgetIcons.items():
        if i == icon:
            del _widgetIcons[k]
###########################
######  instances       ###
###########################

def showAllWidgets(): # move to redRObjects
        for k, i in _widgetInstances.items():
            i.show()
def closeAllWidgets():
    for k, i in _widgetInstances.items():
        i.close()
        
def addInstance(sm, info, settings, insig, outsig, id = None):
    global _widgetInstances
    global _widgetIcons
    global _widgetInfo
    print 'adding instance'
    m = __import__(info.fileName)
    instance = m.__dict__[info.widgetName].__new__(m.__dict__[info.widgetName],
    _owInfo = redREnviron.settings["owInfo"],
    _owWarning = redREnviron.settings["owWarning"],
    _owError = redREnviron.settings["owError"],
    _owShowStatus = redREnviron.settings["owShow"],
    _packageName = info.packageName)
    instance.__dict__['_widgetInfo'] = info
    
    if info.name == 'Dummy': 
        print 'Loading dummy step 3'
        instance.__init__(signalManager = sm,
        forceInSignals = insig, forceOutSignals = outsig)
    else: instance.__init__(signalManager = sm)
    
    instance.loadGlobalSettings()
    if settings:
        instance.setSettings(settings)
        if '_customSettings' in settings.keys():
            instance.loadCustomSettings(settings['_customSettings'])
        else:
            instance.loadCustomSettings(settings)

    instance.setProgressBarHandler(activeTab().progressBarHandler)   # set progress bar event handler
    instance.setProcessingHandler(activeTab().processingHandler)
    #instance.setWidgetStateHandler(self.updateWidgetState)
    #instance.setEventHandler(self.canvasDlg.output.widgetEvents)
    instance.setWidgetWindowIcon(info.icon)
    #instance.canvasWidget = self
    instance.widgetInfo = info
    print 'adding instance'
    if id == None:
        id = instance.widgetID
    else:
        instance.widgetID = id
    _widgetInstances[id] = instance
    
    return instance.widgetID
def getWidgetInstanceByID(id):
    global _widgetInstances
    return _widgetInstances[id]

def instances(wantType = 'list'):
    global _widgetInstances
    if wantType == 'list':## return all of the instances in a list
        return [w for (k, w) in _widgetInstances.items()]
    else:
        return _widgetInstances
def removeWidgetInstanceByID(id):
    import sip
    sip.delete(getWidgetInstanceByID(id))
    del _widgetInstances[id]
###########################
######  lines           ###
###########################

def getLinesByTab(tabs = None):
    global _lines
    global _canvasScene
    if tabs == None:
        tabs = _canvasScene.keys()
    if type(tabs) != list:
        tabs = [tabs]
    tabLinesList = {}
    for t in tabs:
        lineList = []
        for k, li in _lines.items():
            if li.tab == t:
                lineList.append(li)
        tabLinesList[t] = lineList
    return tabLinesList

def getLinesByInstanceIDs(outInstance, inInstance):
    __lineList = []
    tempLines = []
    for k, l in _lines.items():
        __lineList.append((l, l.outWidget, l.inWidget))
    for ll in __lineList:
        if (ll[1].instanceID == outInstance) and (ll[2].instanceID == inInstance):
            tempLines.append(ll[0])
    return tempLines
    
def getLine(outIcon, inIcon):  ## lines are defined by an in icon and an out icon.  there should only be one valid combination in the world.
    __lineList = []
    for k, l in _lines.items():
        __lineList.append((l, l.outWidget, l.inWidget))
    for ll in __lineList:
        if (ll[1].instanceID == outIcon.instanceID) and (ll[2].instanceID == inIcon.instanceID):
            return ll[0]
    return None
def addCanvasLine(outWidget, inWidget, doc, enabled = -1):
    line = orngCanvasItems.CanvasLine(doc.signalManager, doc.canvasDlg, doc.activeTab(), outWidget, inWidget, doc.activeCanvas(), activeTabName())
    _lines[str(time.time())] = line
    if enabled:
        line.setEnabled(1)
    else:
        line.setEnabled(0)
    line.show()
    outWidget.addOutLine(line)
    outWidget.updateTooltip()
    inWidget.addInLine(line)
    inWidget.updateTooltip()
    return line
def addLine(outWidget, inWidget, outSignalName, inSignalName, doc, enabled = 1, process = True, loading = False):
        #if outWidget.instance().outputs.getSignal(outSignalName) in inWidget.instance().inputs.getLinks(inSignalName): return ## the link already exists
            
        
        if inWidget.instance().inputs.getSignal(inSignalName):
            if not inWidget.instance().inputs.getSignal(inSignalName)['multiple']:
                ## check existing link to the input signal
                
                existing = inWidget.instance().inputs.getLinks(inSignalName)
                for l in existing:
                    l['parent'].outputs.removeSignal(inWidget.instance().inputs.getSignal(inSignalName), l['sid'])
                    removeLine(l['parent'], inWidget.instance(), l['sid'], inSignalName)
                
        line = getLine(outWidget, inWidget)
        if not line:
            line = addCanvasLine(outWidget, inWidget, doc, enabled = enabled)
        
        ok = outWidget.instance().outputs.connectSignal(inWidget.instance().inputs.getSignal(inSignalName), outSignalName, process = process)#    self.signalManager.addLink(outWidget, inWidget, outSignalName, inSignalName, enabled)
        if not ok and not loading:
            removeLine(outWidget.instance(), inWidget.instance(), outSignalName, inSignalName)
            ## we should change this to a dialog so that the user can connect the signals manually if need be.
            QMessageBox.information( self, "Red-R Canvas", "Unable to add link. Something is really wrong; try restarting Red-R Canvas.", QMessageBox.Ok + QMessageBox.Default )
            

            return 0
        elif not ok:
            return 0
        # else:
            # orngHistory.logAddLink(self.schemaID, outWidget, inWidget, outSignalName)
        line.updateTooltip()
        
        import redRHistory
        redRHistory.addConnectionHistory(outWidget, inWidget)
        redRHistory.saveConnectionHistory()
        return 1
        
def removeLine(outWidgetInstance, inWidgetInstance, outSignalName, inSignalName):
    outWidgetInstance.outputs.removeSignal(inWidgetInstance.inputs.getSignal(inSignalName), outSignalName)
    
    if not outWidgetInstance.outputs.signalLinkExists(inWidgetInstance): ## move through all of the icons and remove all lines connecting.
        ows = getIconByIconInstanceRef(outWidgetInstance)
        iws = getIconByIconInstanceRef(inWidgetInstance)
        for o in ows:
            for i in iws:
                line = getLine(o, i)
                if line:
                    removeLineInstance(line)
            
            
def removeLineInstance(line):
    obsoleteSignals = line.outWidget.instance().outputs.getSignalLinks(line.inWidget.instance)
    for (s, id) in obsoleteSignals:
        signal = line.inWidget.instance().inputs.getSignal(id)
        line.outWidget.instance().outputs.removeSignal(signal, s)
    for k, l in _lines.items():
        if l == line:
            del _lines[k]   
    line.inWidget.removeLine(line)
    line.outWidget.removeLine(line)
    line.inWidget.updateTooltip()
    line.outWidget.updateTooltip()
    line.remove()
def lines():
    return _lines
###########################
######  instances       ###
###########################