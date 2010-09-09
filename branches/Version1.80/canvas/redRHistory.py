## redRHistory.  Functions and implementations for assessing widget useage and connectivity.  The core of this functionality will be a history file that will represent connections stemming from widgets and to other widgets.  This will be in the form of a dictionary of dictionaries of values.  {widgetA: [(widgetA, c1), (widgetB, c2), ...], widgetB: [(widgetA, c1), (widgetB, c2), ...], ...}.  As new widgets are added using the package manager system this can be modified.

# imports
import cPickle
import os, sys, redREnviron

## get the data into the history dict



try:
    f = open(os.path.join(redREnviron.directoryNames['settingsDir'], 'widgetHistory.rrdf'))
    hDict = cPickle.load(f)
    f.close()
    
except Exception as inst:
    # print inst
    # print 'widgetHistory not found'
    hDict = {}
    
try:
    f = open(os.path.join(redREnviron.directoryNames['settingsDir'], 'widgetHistoryWeb.rrdf'))
    hDictWeb = cPickle.load(f)
    f.close()
except:
    hDictWeb = {}
    
def getTopConnections(newwidget):
    ## return the top connections for the widget
    if newwidget.widgetInfo.fileName in hDict:
        widgetConns = hDict[newwidget.widgetInfo.fileName] # get the info associated with this widget.
        tops = sorted(widgetConns, reverse = True)[1:10]
    else: tops = []
    if newwidget.widgetInfo.outputWidgets:
        tops += [val for val in newwidget.widgetInfo.outputWidgets if val not in tops]
    print tops
    return tops
    
def addConnectionHistory(newwidget, connectingWidget):
    if newwidget.widgetInfo.fileName in hDict:
        widgetConns = hDict[newwidget.widgetInfo.fileName]
    else:
        hDict[newwidget.widgetInfo.fileName] = {}
        widgetConns = hDict[newwidget.widgetInfo.fileName]
    if connectingWidget.widgetInfo.fileName in widgetConns:
        widgetConns[connectingWidget.widgetInfo.fileName] += 1
    else:
        widgetConns[connectingWidget.widgetInfo.fileName] = 1
    
    if newwidget.widgetInfo.fileName in hDictWeb:
        widgetConnsWeb = hDictWeb[newwidget.widgetInfo.fileName]
    else:
        hDictWeb[newwidget.widgetInfo.fileName] = {}
        widgetConnsWeb = hDictWeb[newwidget.widgetInfo.fileName]
    if connectingWidget.widgetInfo.fileName in widgetConnsWeb:
        widgetConnsWeb[connectingWidget.widgetInfo.fileName] += 1
    else:
        widgetConnsWeb[connectingWidget.widgetInfo.fileName] = 1
        
def setTopConnections(newwidgetFileName, hDictElement):
    if newwidgetFileName not in hDict:
        hDict[newwidgetFileName] = {}
        for name in hDictElement:
            hDict[newwidgetFileName][name] = 10
    else:
        for name in hDictElement:
            hDict[newwidgetFileName][name] = 10

def sendConnectionHistory():
    pass
def saveConnectionHistory():
    f = open(os.path.join(redREnviron.directoryNames['settingsDir'], 'widgetHistory.rrdf'), 'w')
    cPickle.dump(hDict, f)
    f.close()