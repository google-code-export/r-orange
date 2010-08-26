


class OutputHandler:
    def __init__(self, parent):                         ## set up the outputHandler, this will take care of sending signals to 
        self.outputSignals = {}
        self.connections = {}
        self.parent = parent # the parent that owns the OutputHandler
    def addOutput(self, id, name, signalClass):
        self.outputSignals[id] = {'name':name, 'signalClass':signalClass, 'connections':{}, 'value':None, 'parent':self.parent}   # set up an 'empty' signal
        
    def connectSignal(self, signal, id, enabled = 1):
        if id not in self.outputSignals.keys():
            raise Exception, 'ID %s does not exist in the outputs of this widget' % (id)
            
        self.outputSignals[id]['connections'][signal['id']] = {'signal':signal, 'enabled':enabled}
        # now send data through
        self._processSingle(self.outputSignals[id], self.outputSignals[id]['connections'][signal['id']])
        return True
    def removeSignal(self, signal, id):
        ## send None through the signal to the handler before we disconnect it.
        if signal['id'] in self.outputSignals[id]['connections'].keys():                                 # check if the signal is there to begin with otherwise we don't do anything
            if self.outputSignals[id]['connections'][signal['id']]['signal']['multiple']:
                self.outputSignals[id]['connections'][signal['id']]['signal']['handler'](
                    #self.outputSignals[signalName]['value'],
                    None,
                    self.parent.widgetID
                    )
            else:
                self.outputSignals[id]['connections'][signal['id']]['signal']['handler'](
                    #self.outputSignals[signalName]['value']
                    None
                    )
            ## remove the signal from the outputSignals
            del self.outputSignals[id]['connections'][signal['id']]
        
    def setOutputData(self, signalName, value):
        self.outputSignals[signalName]['value'] = value
        
    def signalLinkExists(self, widget):
        ## move across the signals and determine if there is a link to the specified widget
        for id in self.outputs.keys():
            for con in self.outputs[id]['connections'].keys():
                if self.outputs[id]['connections'][con]['parent'] == widget:
                    return True
                    
        return False
    def getSignal(self, id):
        if id in self.outputSignals.keys():
            return self.outputSignals[id]
        else:
            return None
    def setSignalEnabled(self, inWidget, enabled):
        for (name, value) in self.outputSignals.items():
            for (conName, conValue) in value['connections'].items():
                if inWidget == conValue['signal']['parent']:
                    conValue['enabled'] = enabled
    def isSignalEnabled(self, inWidget):
        for (name, value) in self.outputSignals.items():
            for (conName, conValue) in value['connections'].items():
                if inWidget == conValue['signal']['parent'] and conValue['enabled']:
                    return True
        return False
    def _processSingle(self, signal, connection):
        if not connection['enabled']: return 0
        handler = connection['signal']['handler']
        multiple = connection['signal']['multiple']
        if signal['signalClass'] in connection['signal']['signalClass']:
            self._handleSignal(signal['value'], handler, multiple)
        else:
            for sig in connection['signal']['signalClass']:
                if sig in signal['signalClass'].convertToList:
                    newVal = signal['signalClass'].convertToClass(sig)
                    self._handleSignal(newVal, handler, multiple)
                    break
                elif signal['signalClass'] in sig.convertFromList:
                    newVal = sig.convertFromClass(signal['value'])
                    self._handleSignal(newVal, handler, multiple)
                    break
    def processData(self, id):
        # collect the signal ID
        signal = self.getSignal(id)
        
        # collect the connections
        connections = signal['connections']
        
        ## handle conversions and send data.
        for cKey in connections.keys():
            self._processSingle(signal, connections[cKey])
            # if not connections[cKey]['signal']['enabled']: continue
            # handler = connections[cKey]['signal']['handler']
            # multiple = connections[cKey]['signal']['multiple']
            # if signal['signalClass'] in connections[cKey]['signal']['signalClass']:
                # self._handleSignal(signal['value'], handler, multiple)
            # else:
                # for sig in connections[cKey]['signal']['signalClass']:
                    # if sig in signal['signalClass'].convertToList:
                        # newVal = signal['signalClass'].convertToClass(sig)
                        # self._handleSignal(newVal, handler, multiple)
                        # break
                    # elif signal['signalClass'] in sig.convertFromList:
                        # newVal = sig.convertFromClass(signal['value'])
                        # self._handleSignal(newVal, handler, multiple)
                        # break
                    
    def _handleSignal(self, value, handler, multiple):
        if multiple:
            handler(value, self.parent.widgetID)
        else:   
            handler(value)
    def hasOutputName(self, name):
        return name in self.outputSignals.keys()
            
class InputHandler:
    def __init__(self, parent):
        self.inputs = {}
        self.parent = parent # the parent widget that owns the InputHandler
    def addInput(self, id, name, signalClass, handler, multiple = False):
        if type(signalClass) not in [list]:
            signalClass = [signalClass]
        self.inputs[id] = {'name':name, 'signalClass':signalClass, 'handler':handler, 'multiple':multiple, 'id':str(id)+'_'+self.parent.widgetID, 'parent':self.parent}
    def getSignal(self, id):
        return self.inputs[id]
    def matchConnections(self, outputHandler):
        ## determine if there are any valid matches between the signal handlers
        for outputKey in outputHandler.outputSignals.keys():
            for inputKey in self.inputs.keys():
                OSignalClass = outputHandler.outputSignals[outputKey]['signalClass']
                for ISignalClass in self.inputs[inputKey]['signalClass']:
                    if OSignalClass == ISignalClass:
                        return True
                    elif ISignalClass in OSignalClass.convertToList:
                        return True
                    elif OSignalClass in ISignalClass.convertFromList:
                        return True
        return False
        
    def getPossibleConnections(self, outputHandler):
        ## determine if there are any valid matches between the signal handlers
        connections = []
        for outputKey in outputHandler.outputSignals.keys():
            for inputKey in self.inputs.keys():
                OSignalClass = outputHandler.outputSignals[outputKey]['signalClass']
                for ISignalClass in self.inputs[inputKey]['signalClass']:
                    if OSignalClass == ISignalClass:
                        connections.append((outputKey, inputKey))
                    elif ISignalClass in OSignalClass.convertToList:
                        connections.append((outputKey, inputKey))
                    elif OSignalClass in ISignalClass.convertFromList:
                        connections.append((outputKey, inputKey))
        return connections
        