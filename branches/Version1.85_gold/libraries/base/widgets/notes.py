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