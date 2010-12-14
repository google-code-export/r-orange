## commitButton (just like button but with a fancy icon)

from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.checkBox import checkBox
import redREnviron
class commitButton(button,widgetState):
    def __init__(self,widget,label, callback = None, processOnInput=None,processOnChange=None,
    disabled=0, icon=None, orientation='horizontal',
    toolTip=None, width = None, height = None, alignment=Qt.AlignRight, toggleButton = False):

        widgetState.__init__(self,widget,label,includeInReports=False)
        icon = str(redREnviron.directoryNames['libraryDir']+'/base/icons/fork.png').replace('\\', '/')

        box = widgetBox(self.controlArea,orientation=orientation,alignment=alignment,includeInReports=False)
        
        box2 = widgetBox(box,orientation='vertical',margin=0,spacing=0)
        if processOnChange is dict:
            self.processOnChangeState = checkBox(box2, label='processOnChange', displayLabel=False,
            buttons = [processOnInput['name']],
            toolTips = [processOnInput['toolTip']]
            )
        elif processOnChange == True:
            self.processOnChangeState = checkBox(box2, label='processOnInput', displayLabel=False,
            buttons = ['Process On Parameter Change'],
            toolTips = ['Try to process as soon as a parameter is changed.']
            )
        
        if processOnInput is dict:
            self.processOnInputState = checkBox(box2, label='processOnInput', displayLabel=False,
            buttons = [processOnInput['name']],
            toolTips = [processOnInput['toolTip']]
            )
        elif processOnInput == True:
            self.processOnInputState = checkBox(box2, label='processOnInput', displayLabel=False,
            buttons = ['Process On Data Input'],
            toolTips = ['Try to process as soon as data is received by the widget. The current state of parameters will be applied.']
            )

        button.__init__(self, widget = box, label = label, callback = callback, disabled = disabled, 
        icon = icon, toolTip = toolTip, width = width, height = 35, 
        toggleButton = toggleButton)
        
        self.setIcon(QIcon(icon))
        self.setIconSize(QSize(20, 20))
        
    def processOnInput(self):
        try:
            if len(self.processOnInputState.getChecked()):
                return True
        except:
            pass
        return False

    def processOnChange(self):
        try:
            if len(self.processOnChangeState.getChecked()):
                return True
        except:
            pass
        return False

    def getSettings(self):
        r = {'processOnInput':self.processOnInput(),'processOnChange':self.processOnChange()}  
        
        return r
    
    def loadSettings(self,data):
        if 'processOnChange' in data.keys() and data['processOnChange']:
            self.processOnChangeState.checkAll()
        if 'processOnInput' in data.keys() and data['processOnInput']:
            self.processOnInputState.checkAll()
        

        
    
    
    