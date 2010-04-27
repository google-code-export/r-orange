import os, sys
from distutils.core import setup
import py2exe

base = 'C:/Users/anup/Documents/red/develop/red/'
sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base,'canvas'))
sys.path.insert(0, os.path.join(base,'OrangeWidgets'))
# sys.path.insert(0, os.path.join(base,'R','bin'))


setup(name="Red-R",
      version="0.1",
      author="Anup  Parikh",
      author_email="anup.parikh@gmail.com",
      url="http://www.red-r.org",
      license="GNU General Public License (GPL)",
      windows=["canvas/red-RCanvas.pyw"],
      options={"py2exe": {
      "skip_archive": True, 
      # "compressed": True, 
      # "bundle_files": 3,
      "excludes": ['R', "Tkconstants","Tkinter","tcl"],
      "includes": ["sip",'OWRpy','OWColorPalette','win32api',
      'OWGraphTools','OWReport','OWToolbars','PyQt4.Qwt5','PyQt4.QtSvg','_rpy2091'],
      'dll_excludes' : ['powrprof.dll', 'API-MS-Win-Core-LocalRegistry_L1-1-0.dll', 'API-MS-Core-ProcessThreads-L1-1-0.dll', 'API-MS-Win-Security-Base-L1-1-0.dll', 'R.dll', 'Rblas.dll', 'Rgraphapp.dll', 'Rinconv.dll', 'Rzlib.dll', 'tcl85.dll', 'tk85.dll', 'R\*']
      }})

      
      
# import sys
# from cx_Freeze import setup, Executable

# executables = [
        # Executable("OrangeCanvas/red-RCanvas.pyw",base = "Win32GUI"),
# ]

# buildOptions = dict(
        # compressed = True,
        # includes = ['sip'],
        # path = sys.path + ["OrangeCanvas","OrangeWidgets"])
        

# setup(
        # name = "advanced_cx_Freeze_sample",
        # version = "0.1",
        # description = "Advanced sample cx_Freeze script",
        # options = dict(build_exe = buildOptions),
        # executables = executables)

