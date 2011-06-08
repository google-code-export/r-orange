"""
.. helpdoc::
<p><!-- [REQUIRED] A detailed description of the widget and what it does--></p>
"""

"""
<widgetXML>    
    <name>Dummy</name>
    <icon>dummy.png</icon>
    <tags> 
        <tag>R</tag> 
    </tags>
    <summary>A special widget that takes the place of any widget that fails during session load.</summary>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
</widgetXML>
"""

"""
<name>Dummy</name>
<tags>R</tags>
<icon>dummy.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI
import redRi18n
_ = redRi18n.get_(package = 'base')
class dummy(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        print unicode(forceInSignals) +' and ' + unicode(forceOutSignals) + ' appending to dummy'
        if 'forceInSignals' in kwargs: 
            import signals
            for (a, b) in [signal for signal in kwargs['forceInSignals']]:
                print 'Appending ' + unicode(a) + ' in dummy to the '+unicode(b)+' signal'
                self.inputs.addInput((a, a, b, None))
        if 'forceOutSignals' in kwargs:
            import signals
            for (a, b) in [signal for signal in  kwargs['forceOutSignals']]:
                print 'Appending ' +unicode(a)+' in dummy using the '+unicode(b)+' signal'
                self.outputs.addOutput((a, a, b))
        print self.inputs
        print self.outputs
            
        box = redRGUI.base.groupBox(self.controlArea, label=_("Info"))
        self.infoa = redRGUI.base.widgetLabel(box, _("A widget failed to load this was put in it's place."))
        self.infob = redRGUI.base.widgetLabel(box, _("The variables that were saved with this widget are %s .\n You can use R Executor to retrieve these variables and incorporate them into your schema.") % str(self.linksOut))
        
    