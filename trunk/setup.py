# red-r linux setup.  Several things we need to do here.

# imports

import sys, os, subprocess

# install the required files
os.system("apt-get install python-qt4")
os.system("apt-get install python-docutils")
os.system("apt-get install python-numpy")
os.system("apt-get install python-qwt5-qt4")
os.system('apt-get install python-rpy python-dev python-numarray-ext python-numeric-ext python-matplotlib python-qt4-dev libqwt5-qt4-dev pyqt4-dev-tools sip4 python-qwt5-qt4')

# install the rpy3 and conversion libraries
os.system("python rpy3-setup/setup.py build")
import platform
if platform.architecture()[0] == "64bit":
    os.system("cp -r rpy3-setup/build/lib.linux*/rpy3 linux64/rpy3")
else:
    os.system("cp -r rpy3-setup/build/lib.linux*/rpy3 linux32/rpy3")
    
os.system("python redrrpy-setup/setup.py build")
import platform
if platform.architecture()[0] == "64bit":
    os.system("cp -r redrrpy-setup/build/lib.linux*/_conversion.so linux64/redrrpy/_conversion.so")
else:
    os.system("cp -r redrrpy-setup/build/lib.linux*/_conversion.so linux32/redrrpy/_conversion.so")

# output the shell script file
with open("/usr/bin/RedR", 'w') as f:
    f.write("""
#!/bin/bash
# Shell wrapper for R executable.

python %s/canvas/red-RCanvas.pyw""" % os.path.abspath(os.path.split(sys.argv[0])[0]))
    f.close()
    
os.system('chmod 755 /usr/bin/RedR')