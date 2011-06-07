"""
This button is similar to :mod:`libraries.base.qtWidgets.button`, but is reserved for executing the main
function of a widget. Includes some helper checkboxes such as allowing the widget to run on receiving input
or any user change.

The commitButton is a special button used for widget commits.  This works just like a regular button but with some additional features that make it quite useful for sending data to be processed.  In addition to a button with a standard icon for users to remember, the commitButton also includes two optional checkboxes.  The state of these checkboxes cam be called using the functions processOnInput() and processOnChange().

Of course the widget must be set up to use these but it is quite easy to write

.. code-block:: python
    
    def processData(self, data):
        if data:
            self.RFunctionParam_data = data.getData()
            if self.RRWidgetGUI_CommitButton.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            
"""

from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.checkBox import checkBox
import redREnviron
import redRi18n
_ = redRi18n.get_(package = 'base')
class commitButton(button,widgetState):
    def __init__(self,widget,label = _('Commit'), callback = None, processOnInput=None,processOnChange=None,
    icon=None, orientation='horizontal',
    width = None, height = None, alignment=Qt.AlignRight, toggleButton = False,**kwargs):
        kwargs.setdefault('includeInReports', False)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        widgetState.__init__(self,widget,label,**kwargs)
        icon = str(redREnviron.directoryNames['libraryDir']+'/base/icons/fork.png').replace('\\', '/')

        box = widgetBox(self.controlArea,orientation=orientation,alignment=alignment,includeInReports=False)
        
        box2 = widgetBox(box,orientation='vertical',margin=0,spacing=0)
        if processOnChange is dict:
            self.processOnChangeState = checkBox(box2, label=_('processOnChange'), displayLabel=False,
            buttons = [processOnInput['name']],
            toolTips = [processOnInput['toolTip']]
            )
        elif processOnChange == True:
            self.processOnChangeState = checkBox(box2, label=_('processOnChange'), displayLabel=False,
            buttons = [_('Process On Parameter Change')],
            toolTips = [_('Try to process as soon as a parameter is changed.')]
            )
        
        if processOnInput is dict:
            self.processOnInputState = checkBox(box2, label=_('processOnInput'), displayLabel=False,
            buttons = [processOnInput['name']],
            toolTips = [processOnInput['toolTip']]
            )
        elif processOnInput == True:
            self.processOnInputState = checkBox(box2, label=_('processOnInput'), displayLabel=False,
            buttons = [_('Process On Data Input')],
            toolTips = [_('Try to process as soon as data is received by the widget. The current state of parameters will be applied.')]
            )

        button.__init__(self, widget = box, label = label, callback = callback, 
        icon = icon, toolTip = toolTip, width = width, height = 35, 
        toggleButton = toggleButton)
        
        self.setIcon(QIcon(icon))
        self.setIconSize(QSize(20, 20))
        
    def processOnInput(self):
        """
        Check if the process on input checkbox is checked. 
        Only applicable if processOnInput is True in init.
        """
        try:
            if len(self.processOnInputState.getChecked()):
                return True
        except:
            pass
        return False

    def processOnChange(self):
        """
        Check if the process on change checkbox is checked. 
        Only applicable if processOnChange is True in init.
        """
        try:
            if len(self.processOnChangeState.getChecked()):
                return True
        except:
            pass
        return False

    def getSettings(self):
        """Save qtWidget state"""
        r = {'processOnInput':self.processOnInput(),'processOnChange':self.processOnChange()}  
        
        return r
    
    def loadSettings(self,data):
        """Load qtWidget state"""
        if 'processOnChange' in data.keys() and data['processOnChange']:
            self.processOnChangeState.checkAll()
        if 'processOnInput' in data.keys() and data['processOnInput']:
            self.processOnInputState.checkAll()
        

        
    
    
    