


class OutputHandler:
    def __init__(self):
        self.outputSignals = {}
        self.connections = {}
        
    def addOutput(self, id, name, signalClass, widget):
        self.outputSignals[id] = {'name':name, 'signalClass':signalClass, 'connections':{}, 'value':None, 'uniqueID':widget.widgetID}
        
    def connectSignal(self, signal, id, enabled = 1):
        if id not in self.outputSignals.keys():
            raise Exception, 'ID %s does not exist in the outputs of this widget' % (id)
            
        self.outputSignals[id]['connections'][signal['id']] = {'signal':signal, 'enabled':enabled}
        
    def removeSignal(self, signal, id):
        ## send None through the signal to the handler before we disconnect it.
        if self.outputSignals[id]['connections'][signal['id']]['multiple']:
            self.outputSignals[id]['connections'][signal['id']]['handler'](
                #self.outputSignals[signalName]['value'],
                None,
                self.outputSignals[signalName]['uniqueID']
                )
        else:
            self.outputSignals[id]['connections'][signal['id']]['handler'](
                #self.outputSignals[signalName]['value']
                None
                )
        ## remove the signal from the outputSignals
        del self.outputSignals[id]['connections'][signal['id']]
        
    def setOutputData(self, signalName, value):
        self.outputSignals[signalName]['value'] = value
        
class InputHandler:
    def __init__(self):
        self.inputs = {}
        
    def addInput(self, id, name, signalClass, handler, multiple = False):
        self.inputs[id] = {'name':name, 'signalClass':signalClass, 'handler':handler, 'multiple':multiple}