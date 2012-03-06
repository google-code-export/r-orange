"""
.. helpdoc::

"""

"""
<widgetXML>    
    <name>Notes</name>
    <icon>notes.png</icon>
    <tags> 
        <tag>R</tag> 
    </tags>
    <summary></summary>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
</widgetXML>
"""

"""
<name>Notes</name>
<tags>R</tags>
<icon>notes.png</icon>
"""

from OWRpy import *
import redRGUI, signals


class notes(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.controlArea.layout().addWidget(self.notesBox)