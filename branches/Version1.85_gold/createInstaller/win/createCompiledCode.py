import os, sys

base = sys.argv[2]

#'C:/Users/anup/Documents/red/develop/makeInstallers/code/red-trunk'
# ...
# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

sys.argv = ['createCompiledCode.py','py2exe']
from distutils.core import setup
import py2exe,shutil

##cleanup
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists(os.path.join(base,'dist')):
    shutil.rmtree(os.path.join(base,'dist'))

includesDir = 'C:/Users/anup/Documents/red/develop/makeInstallers/includes'
sys.path.insert(0, includesDir)
sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base,'canvas'))
sys.path.insert(0, os.path.join(base,'win32'))

import glob
files = [os.path.basename(x).split('.')[0] for x in glob.glob(os.path.join(base,'canvas','*.py'))]
# print files
setup(name="Red-R",
      version="0.2",
      author="Anup  Parikh",
      author_email="anup@red-r.org",
      url="http://www.red-r.org",
      license="GNU General Public License (GPL)",
      windows=[os.path.join(base,"canvas","red-RCanvas.pyw")],
      #data_files = dataFiles,
      options={"py2exe": {
      "dist_dir": os.path.join(base,'dist'),
      "skip_archive": True, 
      # "compressed": True, 
      # "bundle_files": 3,
      "excludes": ['R', "Tkconstants","Tkinter","tcl",'libraries','rpy2'],
      "includes": ["sip",'OWRpy','OWColorPalette','win32api','docutils','win32com','win32com.shell',
      'win32com.shell','OWGraphTools','PyQt4.QtNetwork','PyQt4.Qwt5','PyQt4.QtSvg'] + files,
      'dll_excludes' : ['powrprof.dll', 'API-MS-Win-Core-LocalRegistry_L1-1-0.dll', 'API-MS-Core-ProcessThreads-L1-1-0.dll', 'API-MS-Win-Security-Base-L1-1-0.dll', 'R.dll', 'Rblas.dll', 'Rgraphapp.dll', 'Rinconv.dll', 'Rzlib.dll', 'tcl85.dll', 'tk85.dll', 'R\*']
      }})

# shutil.rmtree(os.path.join(base,'dist','win32'),True)
# shutil.copytree(os.path.join(base,'win32'),os.path.join(base,'dist','win32'))
shutil.rmtree(os.path.join(base,'dist','docutils'),True)
shutil.copytree(os.path.join(includesDir,'docutils','docutils'),os.path.join(base,'dist','docutils'))

for x in glob.glob(os.path.join(base,'canvas','*.py')):
    shutil.copyfile(x,os.path.join(base,'dist',os.path.basename(x)))

import os, fnmatch


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


for filename in find_files(base, '.svn'):
    print 'Found C source:', filename
