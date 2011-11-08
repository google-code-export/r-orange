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
print 'start robjects'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
# print 'after qt'
import orngCanvasItems
# print 'after canvasitems'
import redREnviron
# print 'after enrivon'
import orngView, time, orngRegistry, OWRpy, math
# print 'after orngview'
import redRLog, redRStyle
# print 'after log'
#from orngSignalManager import SignalManager
from orngDlgs import SignalDialog
#sm = SignalManager()

import redRi18n
print 'after imports'
_ = redRi18n.Coreget_()
defaultTabName = _('General')
_widgetRegistry = {}
_lines = {}
_links = {}
_widgetIcons = {defaultTabName:[]}
_widgetInstances = {}
_canvasTabs = {}
_canvasView = {}
_canvasScene = {}
_activeTab = ''
schemaDoc = None
canvasDlg = None
def setSchemaDoc(doc):
    global schemaDoc
    schemaDoc = doc
def setCanvasDlg(dlg):
    global canvasDlg
    canvasDlg = dlg
def readCategories(force = False):
    global _widgetRegistry
    _widgetRegistry = orngRegistry.readCategories(force)

def widgetRegistry():
    """Returns the widget registry.  This is imported by orngRegistry and is a dict with the structure:
    
    {'widgets':[],  # widgets are a list tuple in the form [(widgetID, widgetInfo), ...]
    'templates':[], # templates are a list tuple in the form [(filename, templateInfo), ...]
    'tags': None}   # tags is the tag structure that is used for the widget tree view.
    """
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
    _canvasView[tabname] = orngView.SchemaView(parent, tabname, _canvasScene[tabname], w)
    w.layout().addWidget(_canvasView[tabname])
    _activeTab = tabname
    _widgetIcons[tabname] = []
    return w
    
# def removeTabView(tabname, parent):
    
def activeTab():
    global _activeTab
    global _canvasView
    return _canvasView[_activeTab]

def scenes():
    global _canvasScene
    return [s for k, s in _canvasScene.items()]
def views():
    global _canvasView
    return _canvasView.values()
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
    _widgetIcons[tabName] = []
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
    del _widgetIcons[tabname]
    #del _canvas[tabname]
    #del _canvasTabs[tabname]
    
    
###############################
#######     icons       #######
###############################

def getCompatibleWidgets(icon):
    fn = icon.widgetInfo.fileName
    info = _widgetRegistry['widgets'][fn]
    outputs = info.outputs
    oAdd = []
    for o in outputs:
        if o[0] not in _widgetRegistry['signals']: continue
        oAdd += _widgetRegistry['signals'][o[0]]['convertTo']
    outputs += oAdd
    outputs = [o[0] for o in outputs]
    inputs = info.inputs
    iAdd = []
    for i in inputs:
        if i[0] not in _widgetRegistry['signals'] or i[0] == '': continue
        iAdd += _widgetRegistry['signals'][i[0]]['convertFrom']
    inputs += iAdd
    inputs = [i[0] for i in inputs]
    
    topcon = {'inputs':[], 'outputs':[]}
    for w in _widgetRegistry['widgets']:
        tempout = [o[0] for o in _widgetRegistry['widgets'][w].outputs if o[0] != '']
        fullout = tempout
        for o in tempout:
            if o not in _widgetRegistry['signals'] or o == '': continue
            fullout += _widgetRegistry['signals'][o]['convertTo']
        
        #print fullout
        tempin = [i[0] for i in _widgetRegistry['widgets'][w].inputs if i[0] != '']
        fullin = tempin
        for i in tempin:
            if i not in _widgetRegistry['signals']: continue
            fullin += _widgetRegistry['signals'][i]['convertFrom']
        #print fullin
        for i in inputs: 
            if i in fullout: 
                topcon['inputs'].append(_widgetRegistry['widgets'][w])
                break
        for o in outputs:
            if o in fullin:
                topcon['outputs'].append(_widgetRegistry['widgets'][w])
                break
    return topcon
            
            
def getIconsByTab(tabs = None):  # returns a dict of lists of icons for a specified tab, if no tab specified then all incons on all tabs are returned.
    global _widgetIcons
    global _canvasScene
    if tabs == None:
        tabs = _canvasScene.keys()
    if type(tabs) != list:
        tabs = [tabs]
    #print tabs, _('Tabs')
    tabIconsList = {}
    for t in tabs:
        tabIconsList[t] = _widgetIcons[t]
    return tabIconsList

def getWidgetByInstance(instance): 
    """This function returns an icon matching the instance of the sent instance.  This can indicate if a widget is matched with an icon or not to prevent lost widgets from cluttering the session.""" 
    global _widgetIcons
    for t in _widgetIcons.values():
        for widget in t:
            if widget.instance() == instance:
                return widget
    else:
        redRLog.log(redRLog.REDRCORE, redRLog.WARNING, 'Unable to find a matching widget instance %s' % str(instance))
        raise Exception(_('Widget %s not found in %s') % (instance, _widgetIcons))
    
def newIcon(canvas, tab, info, pic, dlg, instanceID, tabName):
    if getWidgetByIDActiveTabOnly(instanceID):
        return getWidgetByIDActiveTabOnly(instanceID)
    newwidget = orngCanvasItems.CanvasWidget(canvas, tab, info, pic, dlg, instanceID = instanceID, tabName = tabName)
    
    _widgetIcons[tabName].append(newwidget) # put a new widget into the stack with a timestamp.
    return newwidget
    
def getIconIDByIcon(icon):
    for k, i in _widgetIcons.items():
        if i == icon:
            return k
    return None

def getIconByIconID(wid):
    return _widgetIcons[wid]
    
def getIconByIconCaption(caption):
    icons = []
    for t in _widgetIcons.values():
        for i in t:
            if i.caption == caption:
                icons.append(i)
    return icons
    
def getIconByIconInstanceRef(instance):
    icons = []
    for t in _widgetIcons.values():
        for i in t:
            if i.instanceID == instance.widgetID:
                icons.append(i)
    return icons
    
def getIconByIconInstanceID(wid):
    icons = []
    for t in _widgetIcons.values():
        for i in t:
            if i.instanceID == wid:
                icons.append(i)
    return icons
def instanceOnTab(inst, tabName):
    global _widgetIcons
    for t in _widgetIcons.values():
        for i in t:
            if i.instance() == inst and i.tab == tabName:
                return True
    return False
def getWidgetByIDActiveTabOnly(widgetID):
    for t in _widgetIcons.values():
        #print widget.instanceID
        for widget in t:
            if (widget.instanceID == widgetID) and (widget.tab == activeTabName()):
                return widget
    return None
    
def removeWidgetIcon(icon):
    global _widgetIcons
    for t in _widgetIcons.values():
        redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('widget icon values %s') % str(t))
        while icon in t:
            redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('removing widget icon instance %s') % icon)
            t.remove(icon)

#################################
####    Core Widget Functions ###
#################################
def widgets():
    wlist = []
    rolist = getIconsByTab()
    for k, l in rolist.items():
        wlist += l
    return wlist
def resolveCollisions(newwidget, x, y):
    #print 'Resolving collisions'
    if x==-1 or y==-1:
        print 'Getting active tab'
        if activeTab().getSelectedWidgets():
            x = activeTab().getSelectedWidgets()[-1].x() + 110
            y = activeTab().getSelectedWidgets()[-1].y()
        elif widgets() != []:
            x = widgets()[-1].x() + 110  # change to selected widget 
            y = widgets()[-1].y()
        else:
            x = 30
            y = 50
    #print 'Setting Coords'
    newwidget.setCoords(x, y)
    # move the widget to a valid position if necessary
    invalidPosition = (activeTab().findItemTypeCount(activeCanvas().collidingItems(newwidget), orngCanvasItems.CanvasWidget) > 0)
    #print 'Invalid Position located'
    if invalidPosition:
        for r in range(50, 300, 50):
            for fi in [90, -90, 0, 45, -45]:
                xOff = r * math.cos(math.radians(fi))
                yOff = r * math.sin(math.radians(fi))
                rect = QRectF(x+xOff-20, y+yOff-20, 75, 75)
                invalidPosition = activeTab().findItemTypeCount(activeCanvas().items(rect), orngCanvasItems.CanvasWidget) > 0
                if not invalidPosition:
                    newwidget.setCoords(x+xOff, y+yOff)
                    break
            if not invalidPosition:
                break
    #print 'Collisions Resolved'
def addWidget(widgetInfo, x= -1, y=-1, caption = "", widgetSettings = None, saveTempDoc = True, forceInSignals = None, forceOutSignals = None, wid = None):
    """A core function to expose widget addition to the rest of core.  Taken over from :mod:`orngDoc`.
    .. note::
        The function in :mod:`orngDoc` is still active but will soon be depricated for this function.
    """
    #global sm
    global canvasDlg
    qApp.setOverrideCursor(Qt.WaitCursor)
    try:
        instanceID = addInstance(widgetInfo, widgetSettings, forceInSignals, forceOutSignals, wid = wid)
        caption = widgetInfo.name
        if getIconByIconCaption(caption):
            i = 2
            while getIconByIconCaption('%s (%s)' % (caption, str(i))): i += 1
            caption = '%s (%s)' % (caption, str(i))
        
        newwidget = newIcon(activeCanvas(), activeTab(), widgetInfo, redRStyle.defaultWidgetIcon, canvasDlg, instanceID = instanceID, tabName = activeTabName())
        newwidget.caption = caption
        newwidget.updateText(caption)
        redRLog.log(redRLog.REDRCORE, redRLog.INFO, _('Create new widget named %s.') % newwidget.caption)
    except:
        redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
        qApp.restoreOverrideCursor()
        return None
        
    resolveCollisions(newwidget, x, y)
    newwidget.instance().setWindowTitle(newwidget.caption)
    activeCanvas().update()
    
    try:
        #sm.addWidget(newwidget.instance())
        newwidget.show()
        newwidget.updateTooltip()
        newwidget.setProcessing(1)
        # if redREnviron.settings["saveWidgetsPosition"]:
            # newwidget.instance().restoreWidgetPosition()
        newwidget.setProcessing(0)
    except:
        redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            
    qApp.restoreOverrideCursor()
    return newwidget.instanceID

###########################
######  instances       ###
###########################

def showAllWidgets(): # move to redRObjects
        for k, i in _widgetInstances.items():
            i.show()
def closeAllWidgets():
    for k, i in _widgetInstances.items():
	#print 'closing widget %s' % k
        try:
            i.close()
        except Exception as inst:
            pass
        
def addInstance(info, settings, insig, outsig, wid = None):
    """Called to add an instance of a widget to the canvas."""
    global _widgetInstances
    global _widgetIcons
    global _widgetInfo
    m = __import__(info.fileName)
    instance = m.__dict__[info.widgetName].__new__(m.__dict__[info.widgetName],
    _owInfo = redREnviron.settings["owInfo"],
    _owWarning = redREnviron.settings["owWarning"],
    _owError = redREnviron.settings["owError"],
    _owShowStatus = redREnviron.settings["owShow"],
    _packageName = info.packageName)
    instance.__dict__['_widgetInfo'] = info
    if wid == None:
        OWRpy.uniqueWidgetNumber += 1
        ctime = unicode(time.time())
        wid = unicode(OWRpy.uniqueWidgetNumber) + '_' + ctime
    #redRLog.log(redRLog.REDRCORE, redRLog.DEBUG,redRLog.formatException())    
    redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('adding instance number %s name %s') % (str(wid), info.name))
    if info.name == 'Dummy': 
        instance.__init__(forceInSignals = insig, forceOutSignals = outsig, wid = wid)
    else: instance.__init__(wid = wid)
    
    ## check if an id is present, if this is the case then we should set the id to the widget.
    
            

    instance.setProgressBarHandler(activeTab().progressBarHandler)   # set progress bar event handler
    instance.setProcessingHandler(activeTab().processingHandler)
    instance.setWidgetWindowIcon(info.icon)
    #instance.canvasWidget = self
    instance.widgetInfo = info
    redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('instance ID is %s') % instance.widgetID)
    if wid in _widgetInstances.keys():
        redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('id was found in the keys, placing as new ID'))
        ## this is interesting since we aren't supposed to have this, just in case, we throw a warning
        redRLog.log(redRLog.REDRCORE, redRLog.WARNING, _('Warning: widget id already in the keys, setting new widget instance'))
        wid = unicode(time.time())
        instance.widgetID = wid
        instance.variable_suffix = '_' + instance.widgetID
        instance.resetRvariableNames()
    if not instance:
        raise Exception(_('Error in loading widget %s') % wid)
    _widgetInstances[wid] = instance
    
    # setting the settings should be the last thing that we do since this is a change of the widget data and may depend on access to the registry.
    instance.loadGlobalSettings()
    if settings:
        try:
            instance.setSettings(settings)
            instance.loadCustomSettings(settings)
        except Exception as inst:
            # print '##########################\n'*5 
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, _('redRObjects addInstance; error in setting settings or custom settings. <b>%s<b>') % inst)
            redRLog.log(redRLog.REDRCORE, redRLog.DEBUG,redRLog.formatException())
    
    return wid
def getWidgetInstanceByID(wid):
    global _widgetInstances
    #redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, 'Loading widget %s keys are %s' % (id, _widgetInstances.keys()))
    try:
        return _widgetInstances[wid]
    except Exception as inst:
        redRLog.log(redRLog.REDRCORE, redRLog.ERROR, _('Error in locating widget %s, available widget ID\'s are %s' % (wid, _widgetInstances.keys())))
def getWidgetInstanceByTempID(wid):
    global _widgetInstances
    for w in _widgetInstances.values():
        if w.tempID == wid:
            return w
def instances(wantType = 'list'):
    global _widgetInstances
    if wantType == 'list':## return all of the instances in a list
        redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('Widget instances are %s') % unicode(_widgetInstances.values()))
        return _widgetInstances.values()
    else:
        return _widgetInstances
def removeWidgetInstanceByID(wid):
    try:
        widget = getWidgetInstanceByID(wid)
        removeWidgetInstance(widget)
        del _widgetInstances[wid]
        
        
    except Exception as inst: 
        redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, 'Failed to remove the widget instance %s, %s' % (wid, unicode(inst)))

def removeWidgetInstance(widget):
    redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('Removing widget instance %s') % widget)
    widget.onDeleteWidget()
    import sip
    sip.delete(widget)
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
        if (ll[1] == outIcon) and (ll[2] == inIcon):
            return ll[0]
    return None
def addCanvasLine(outWidget, inWidget, enabled = -1):
    global schemaDoc
    #redRLog.log(redRLog.REDRCORE, redRLog.INFO, _('Adding canvas line'))
    line = orngCanvasItems.CanvasLine(schemaDoc.canvasDlg, schemaDoc.activeTab(), outWidget, inWidget, schemaDoc.activeCanvas(), activeTabName())
    _lines[unicode(time.time())] = line
    if enabled:
        line.setEnabled(1)
        #print 'setting line enabled'
    else:
        line.setEnabled(0)
        #print 'setting line disabled'
    line.show()
    outWidget.addOutLine(line)
    outWidget.updateTooltip()
    inWidget.addInLine(line)
    inWidget.updateTooltip()
    return line
def addLine(outWidgetInstance, inWidgetInstance, enabled = 1):
        global schemaDoc
        # redRLog.log(redRLog.REDRCORE, redRLog.INFO, 'Adding line outWidget %s, inWidget %s' % (
        # outWidgetInstance.caption, inWidgetInstance.caption))
        ## given an out and in instance connect a line to all of the icons with those instances.
        tabIconStructure = getIconsByTab()
        ot = activeTabName()
        owi = outWidgetInstance
        iwi = inWidgetInstance
        #print 'owi', owi
        #print 'iwi', iwi
        redRLog.log(redRLog.REDRCORE, redRLog.INFO, 'instances %s, %s' % (str(owi), str(iwi)))
        for tname, icons in tabIconStructure.items():
            schemaDoc.setTabActive(tname)
            o = None
            i = None
            
            for ic in icons:
                #print 'icon', ic
                #print 'icon instance', ic.instance()
                if ic.instance() == iwi:
                    i = ic
                    redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('found in widget %s') % str(ic))
                if ic.instance() == owi:
                    o = ic
                    redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('found out widget %s') % str(ic))
            if i!= None and o != None:  # this means that there are the widget icons in question in the canvas so we should add a line between them.
                line = getLine(o, i)
                redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('the matching line is %s') % str(line))
                if not line:
                    line = addCanvasLine(o, i, enabled = enabled)
                    line.refreshToolTip()
            
        schemaDoc.setTabActive(ot)
        updateLines()
        return 1
def removeLine(outWidgetInstance, inWidgetInstance, outSignalName = None, inSignalName = None):
        """This function removes the line between outWidgetInstance and inWidgetInstance.  It moves across all icons to identify icons that share an underlying widget instance."""
        redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('Removing Line'))
        tabIconStructure = getIconsByTab()
        owi = outWidgetInstance
        iwi = inWidgetInstance
        for tname, icons in tabIconStructure.items():
            
            o = None
            i = None
            for ic in icons:
                if ic.instance() == iwi:
                    i = ic
                if ic.instance() == owi:
                    o = ic
                    
            if i!= None and o != None:  # this means that there are the widget icons in question in the canvas so we should add a line between them.
                line = getLine(o, i)
                if line:
                    removeLineInstance(line)
            
            
def removeLineInstance(line):
    """This function removes all links between two widgets and also removes the line instance.  This is called to remove any line instances."""
    
    import redRSignalManager
    obsoleteSignals = redRSignalManager.getLinksByWidgetInstance(line.outWidget.instance(), line.inWidget.instance())
    #obsoleteSignals = line.outWidget.instance().outputs.getSignalLinks(line.inWidget.instance())
    redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, _('Removing obsolete signals %s') % unicode(obsoleteSignals))
    redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, 'removing the following signals %s' % unicode(obsoleteSignals))
    for o,i,e,n in obsoleteSignals:
        #signal = line.inWidget.instance().inputs.getSignal(id)
        line.outWidget.instance().outputs.removeSignal(i, o.wid)
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
def updateLines():
    global _lines
    for l in _lines.values():
        l.updateStatus()
def getLinesByWidgetInstanceID(outID, inID):  # must return a list of lines that match the outID and inID.
    global _lines
    tempLines = []
    for k, l in _lines.items():
        if l.outWidget.instanceID == outID and l.inWidget.instanceID == inID:
            tempLines.append(l)
    return tempLines
    
    
### signals ###
def signalFromSettings(d): # d is a dict of settings that we should use to make the new signal.
    import signals
    import imp, redREnviron
    fp, pathname, description = imp.find_module('libraries', [redREnviron.directoryNames['redRDir']])
    varc = imp.load_module('libraries', fp, pathname, description)
    for mod in d['class'].replace("<'", '').replace("'>", '').split('.')[1:]:
       varc = getattr(varc, mod)
    signal = varc(widget = getWidgetInstanceByID(d['wid']), data = d['data'], parent = d['parent'])
    signal.loadSettings(d)
    return signal
       
       

       