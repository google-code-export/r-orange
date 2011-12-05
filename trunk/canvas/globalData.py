###############Define global data###############
#import orngSignalManager

globalData = {}
def _(a):
    return a
def setGlobalData(creatorWidget, name, data, description = None):
    if type(creatorWidget) in [str]:
        widgetID = 'none'
    elif hasattr(creatorWidget, 'widgetID'):
        widgetID = creatorWidget.widgetID
    else:
        widgetID = 'none'
        
    if widgetID not in globalData.keys():
        globalData[widgetID] = {}
    
    globalData[widgetID][name] = {
    'creator': widgetID, 
    'data':data,
    'description':description
    }

def getGlobalData(name):
        data = []
        for k, v in globalData.items():
            if name in v.keys():
                data.append(v[name])
        return data
    
def globalDataExists(name):
    for key,value in globalData.items():
        if name in value.keys(): 
            return True
    return False
    
def removeGlobalData(creatorWidget,name = None):
    if name:
        if creatorWidget.widgetID in globalData.keys() and name in globalData[creatorWidget.widgetID].keys():
            del globalData[creatorWidget.widgetID][name]
    else:
        if creatorWidget.widgetID in globalData.keys():
            del globalData[creatorWidget.widgetID]
