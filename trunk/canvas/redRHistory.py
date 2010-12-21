## redRHistory.  Functions and implementations for assessing widget useage and connectivity.  The core of this functionality will be a history file that will represent connections stemming from widgets and to other widgets.  This will be in the form of a dictionary of dictionaries of values.  {widgetA: [(widgetA, c1), (widgetB, c2), ...], widgetB: [(widgetA, c1), (widgetB, c2), ...], ...}.  As new widgets are added using the package manager system this can be modified.

# imports
import cPickle, redRObjects
import os, sys, redREnviron,redRLog

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
    
def getSuggestWidgets(outWidget):
    actions = []
    try:
        topCons = getTopConnections(outWidget)
        print topCons
        widgets = redRObjects.widgetRegistry()['widgets']
        for con in topCons:
            if con in widgets.keys():
                wInfo = widgets[con]
                actions.append(wInfo)
    except:
        redRLog.log(redRLog.REDRCORE,redRLog.WARNING,'The widget use history is corrept. Please delete it.')
    return actions
def getTopConnections(outWidget):
    ## return the top connections for the widget
    # print 'filename:', outWidget.widgetInfo.fileName
    # print 'dict', hDict
    if outWidget.widgetInfo.fileName in hDict:
        tops = hDict[outWidget.widgetInfo.fileName]['recent']
        widgetConns = hDict[outWidget.widgetInfo.fileName]['counts'] # get the info associated with this widget.
        tops += [val for val in sorted(widgetConns, key=widgetConns.get, reverse=True)[0:9] if val not in tops]
    else:
        tops = []
    
    if outWidget.widgetInfo.outputWidgets:
        tops += [val for val in outWidget.widgetInfo.outputWidgets if val not in tops and val != '']

    
    return tops
    
def addConnectionHistory(outWidget,inWidget):
    
    if outWidget.widgetInfo.fileName not in hDict:
        hDict[outWidget.widgetInfo.fileName] = {'recent':[], 'counts':{}}
    if 'recent' not in hDict[outWidget.widgetInfo.fileName]:
        hDict[outWidget.widgetInfo.fileName]['recent'] = []
    if 'counts' not in hDict[outWidget.widgetInfo.fileName]:
        hDict[outWidget.widgetInfo.fileName]['counts'] = {}
    
    recent = hDict[outWidget.widgetInfo.fileName]['recent']
    counts = hDict[outWidget.widgetInfo.fileName]['counts']
    
    recent.insert(0,inWidget.widgetInfo.fileName)
    recent = list(set(recent))
    
    # print 'unique recent', recent
    if len(recent)  >2:
        recent.pop()
    hDict[outWidget.widgetInfo.fileName]['recent'] = recent
    
    if inWidget.widgetInfo.fileName in counts:
        counts[inWidget.widgetInfo.fileName] += 1
    else:
        counts[inWidget.widgetInfo.fileName] = 1
    
    print hDict
    
    # if newwidget.widgetInfo.fileName in hDictWeb:
        # widgetConnsWeb = hDictWeb[newwidget.widgetInfo.fileName]
    # else:
        # hDictWeb[newwidget.widgetInfo.fileName] = {}
        # widgetConnsWeb = hDictWeb[newwidget.widgetInfo.fileName]
    # if connectingWidget.widgetInfo.fileName in widgetConnsWeb:
        # widgetConnsWeb[connectingWidget.widgetInfo.fileName] += 1
    # else:
        # widgetConnsWeb[connectingWidget.widgetInfo.fileName] = 1
        
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