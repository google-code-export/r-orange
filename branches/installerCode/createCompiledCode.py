import os, sys
from distutils.core import setup
import py2exe,shutil

sys.path.insert(0, 'C:/Users/anup/Documents/red/develop/makeInstallers/includes')
base = 'C:/Users/anup/Documents/red/develop/makeInstallers/code/Version1.80'
sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base,'canvas'))
sys.path.insert(0, os.path.join(base,'canvas','rpy'))

#dataFiles = [('docutils/writers/odf_odt', ['C:\\Python26/Lib/site-packages/docutils/writers/odf_odt/styles.odt'])]

setup(name="Red-R",
      version="0.1",
      author="Anup  Parikh",
      author_email="anup.parikh@gmail.com",
      url="http://www.red-r.org",
      license="GNU General Public License (GPL)",
      windows=[os.path.join(base,"canvas","red-RCanvas.pyw")],
      #data_files = dataFiles,
      options={"py2exe": {
      "dist_dir": os.path.join(base,'dist'),
      "skip_archive": True, 
      # "compressed": True, 
      # "bundle_files": 3,
      "excludes": ['R', "Tkconstants","Tkinter","tcl",'libraries'],
      "includes": ["sip",'OWRpy','OWColorPalette','win32api','docutils',
      'docutils.parsers.rst.directives.images',
      'docutils.parsers.rst.directives.body',
      'docutils.parsers.rst.directives.html',
      'docutils.parsers.rst.directives.misc',
      'docutils.parsers.rst.directives.parts',
      'docutils.parsers.rst.directives.references',
      'docutils.parsers.rst.directives.tables',
      'docutils.writers',      
      'OWGraphTools','PyQt4.QtNetwork','PyQt4.Qwt5','PyQt4.QtSvg','_rpy2091'],
      'dll_excludes' : ['powrprof.dll', 'API-MS-Win-Core-LocalRegistry_L1-1-0.dll', 'API-MS-Core-ProcessThreads-L1-1-0.dll', 'API-MS-Win-Security-Base-L1-1-0.dll', 'R.dll', 'Rblas.dll', 'Rgraphapp.dll', 'Rinconv.dll', 'Rzlib.dll', 'tcl85.dll', 'tk85.dll', 'R\*']
      }})

shutil.rmtree(os.path.join(base,'dist','docutils'),True)
shutil.copytree('C:\\Python26/Lib/site-packages/docutils',os.path.join(base,'dist','docutils'))
      
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

