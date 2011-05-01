###############Define global data###############
import orngSignalManager

globalData = {}
globalSettings = {}
def _(a):
    return a
def setGlobalData(creatorWidget, name, data, description = None):
    if type(creatorWidget) in [str]:
        widgetID = 'none'
    elif hasattr(creatorWidget, 'widgetID'):
        widgetID = creatorWidget.widgetID
        
    if widgetID not in globalData.keys():
        globalData[widgetID] = {}
    
    globalData[widgetID][name] = {
    'creator': widgetID, 
    'data':data,
    'description':description
    }

def getGlobalData(widget,name):
    if widget != None:
        parents = orngSignalManager.globalSignalManager.getParents(widget)
        parentIDs = [w.widgetID for w in parents]
        data = []
        for key,value in globalData.items():
            if key in parentIDs and  name in value.keys(): 
                data.append(value[name])
        return data
    else:
        data = []
        for k, v in globalData.items():
            if name in v.keys():
                data.append(v[name])
        return data
    
def globalDataExists(widget,name):
    parents = orngSignalManager.globalSignalManager.getParents(widget)
    parentIDs = [w.widgetID for w in parents]
    for key,value in globalData.items():
        if key in parentIDs and  name in value.keys(): 
            return True
    
    return False
    
def removeGlobalData(creatorWidget,name = None):
    if name:
        if creatorWidget.widgetID in globalData.keys() and name in globalData[creatorWidget.widgetID].keys():
            del globalData[creatorWidget.widgetID][name]
    else:
        if creatorWidget.widgetID in globalData.keys():
            del globalData[creatorWidget.widgetID]
        
def setGlobalSettings(name, data):
    if name not in globalSettings.keys():
        globalSettings[name] = []
    globalSettings[name].append(data)
    
def getGlobalSettings(name):
    if name in globalSettings:
        return globalSettings[name]
    else:
        return []
