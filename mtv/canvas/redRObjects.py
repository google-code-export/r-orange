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
    
import orngCanvasItems, redREnviron

widgetRegistry = {}
lines = {}
widgetIcons = {}
widgetInstances = {}
canvasTabs = {}

def readCategories():
    widgetRegistry = orngRegistry.readCategories()

def getIconsByTab(tabs = None):
    if tabs = None:
        tabs = canvasTabs.keys()
    tabIconsList = []
    for t in tabs:
        icons = []
        for k, wi in widgetIcons.items():
            if wi.tab == t:
                icons.append(wi)
        tabIconsList.append(icons)
    return tabIconsList
    
def getLinesByTab(tabs = None):
    if tabs = None:
        tabs = canvasTabs.keys()
    tabLinesList = []
    for t in tabs:
        lineList = []
        for k, li in lines.items():
            if li.tab == t:
                lineList.append(li)
        tabLinesList.append(lineList)
    return tabLinesList

def getLine(outWidget, inWidget):
    for k, l in lines.items():
        if l.outWidget == outWidget and l.inWidget == inWidget:
            return l
    return None
def addLine(outWidget, inWidget, outSignalName, inSignalName, enabled = 1, fireSignal = 1, process = True, loading = False):
        if outWidget.instance().outputs.getSignal(outSignalName) in inWidget.instance().inputs.getLinks(inSignalName): return ## the link already exists
            
        
        if inWidget.instance().inputs.getSignal(inSignalName):
            if not inWidget.instance().inputs.getSignal(inSignalName)['multiple']:
                ## check existing link to the input signal
                
                existing = inWidget.instance().inputs.getLinks(inSignalName)
                for l in existing:
                    l['parent'].outputs.removeSignal(inWidget.instance().inputs.getSignal(inSignalName), l['sid'])
                    removeLink(self.getWidgetByInstance(l['parent']), inWidget, l['sid'], inSignalName)
                
        line = self.getLine(outWidget, inWidget)
        if not line:
            line = orngCanvasItems.CanvasLine(self.signalManager, self.canvasDlg, self.activeTab(), outWidget, inWidget, self.activeCanvas(), self.activeTabName())
            self.lines.append(line)
            if enabled:
                line.setEnabled(1)
            else:
                line.setEnabled(0)
            line.show()
            outWidget.addOutLine(line)
            outWidget.updateTooltip()
            inWidget.addInLine(line)
            inWidget.updateTooltip()
        
        ok = outWidget.instance().outputs.connectSignal(inWidget.instance().inputs.getSignal(inSignalName), outSignalName, process = process)#    self.signalManager.addLink(outWidget, inWidget, outSignalName, inSignalName, enabled)
        if not ok and not loading:
            self.removeLink(outWidget, inWidget, outSignalName, inSignalName)
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