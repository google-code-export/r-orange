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
    <citation>
    <!-- [REQUIRED] -->
        <author>
            <name>Red-R Core Team</name>
            <contact>http://www.red-r.org/contact</contact>
        </author>
        <reference>http://www.red-r.org</reference>
    </citation>
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