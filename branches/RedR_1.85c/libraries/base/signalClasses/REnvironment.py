"""REnvironment
.. helpdoc::
This signal represents a connection to an R environment.  Environments have a more limited scope than the global scope."""

"""
.. convertTo:: ``
.. convertFrom:: ``
"""
from libraries.base.signalClasses.RVariable import *
class REnvironment(RVariable): # R environment class points to an environment within R
    convertFromList = []
    convertToList = []
