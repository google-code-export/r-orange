graphCmd = 'python dep.py %s | dot -T png -o %s.png'

import sys,os,glob,subprocess
import shutil

redRRoot = sys.argv[1]
docRoot = os.path.join(redRRoot, 'doc')
makeDeps = int(sys.argv[2])

# toRM = glob.glob(os.path.join(docRoot,'core','*.rst')) + glob.glob(os.path.join(docRoot,'libraries','*','*','*.rst')) + glob.glob(os.path.join(docRoot,'libraries','*','*.rst')) + glob.glob(os.path.join(docRoot,'libraries','*.rst'))

# for x in toRM: os.remove(x)

shutil.rmtree(os.path.join(docRoot,'core'),True)
os.mkdir(os.path.join(docRoot,'core'))
shutil.rmtree(os.path.join(docRoot,'libraries'),True)
os.mkdir(os.path.join(docRoot,'libraries'))

coreFiles = glob.glob(os.path.join(redRRoot,'canvas','*.py')) + glob.glob(os.path.join(redRRoot,'canvas','*.pyw'))
for n in coreFiles:
    print '%s' % n
    (name,ext) = os.path.splitext(os.path.basename(n))
    
    output = """%s
=================================

.. automodule:: %s
   :members:
   :undoc-members:
   :show-inheritance:
    
""" % (name, name)
    if makeDeps == 1:
        output += """
.. image:: %s.png
""" % name
        cmd = graphCmd % (n,os.path.join(docRoot,'core',name))
        print cmd
        os.system(cmd)
    #print output
    f = open(os.path.join(docRoot,'core',name+'.rst'),'w')
    f.write(output)
    f.close()
    
    

    
#########################################################################


    
packages = glob.glob(os.path.join(redRRoot,'libraries','*','package.xml'))
if not os.path.exists(os.path.join(docRoot, 'libraries')): os.mkdir(os.path.join(docRoot, 'libraries'))

for p in packages:
    package = os.path.split(os.path.split(p)[0])[1]
    if not os.path.exists(os.path.join(docRoot,'libraries',package)):
        os.mkdir(os.path.join(docRoot,'libraries',package))
        os.mkdir(os.path.join(docRoot,'libraries',package,'widgets'))
        os.mkdir(os.path.join(docRoot,'libraries',package,'qtWidgets'))
        os.mkdir(os.path.join(docRoot,'libraries',package,'signalClasses'))
    with open(os.path.join(redRRoot, 'libraries', package, 'package.xml'), 'r') as f:
        xml = f.read()
        
    libraryOut = """%(PACKAGENAME)s Package
=================================

Package XML
~~~~~~~~~~~

%(PACKAGEXML)s

Contents
~~~~~~~~

Widgets:

.. toctree::
   :glob:
   :maxdepth: 2
   
   widgets/*
   
QT Widgets:

.. toctree::
   :glob:
   :maxdepth: 2
   
   qtWidgets/*

Signal Classes:

.. toctree::
   :glob:
   :maxdepth: 2
   
   signalClasses/*
""" % ('PACKANGMANE':package, 'PACKAGEXML':xml)
    f = open(os.path.join(docRoot,'libraries',package,package+'.rst'),'w')
    f.write(libraryOut)
    f.close()
    
###############################################    
    widgets = glob.glob(os.path.join(redRRoot,'libraries',package,'widgets','*.py'))
    try:
        if '__init__.py' not in widgets:
            f = open(os.path.join(docRoot,'libraries',package,'widgets','__init__.py'),'w')
            f.write('')
            f.close()
    except: pass
    for n in widgets:
        print '%s' % n
        (name,ext) = os.path.splitext(os.path.basename(n))
        if name =='__init__': continue
        with open(os.path.join(redRRoot, 'libraries', package, 'meta', 'widgets', name, '.xml'), 'r') as f:
            xml = f.read()
        output = """%(WIDGETNAME)s
=================================

Widget XML
~~~~~~~~~~

%(WIDGETXML)s

Widget TOC
~~~~~~~~~~
   
.. automodule:: libraries.%(PACKAGENAME)s.widgets.%(WIDGETNAME)s
   :members:
   :undoc-members:
   :show-inheritance:
   
.. image:: %(WIDGETNAME)s.png
""" % ('WIDGETNAME':name, 'PACKAGENAME':package, 'WIDGETXML':xml)
            
        f = open(os.path.join(docRoot,'libraries',package,'widgets',name+'.rst'),'w')
        f.write(output)
        f.close()
        
        if makeDeps == 1:
            cmd = graphCmd % (n,os.path.join(docRoot,'libraries',package,'widgets',name))
            os.system(cmd)
###############################################
    qtwidgets = glob.glob(os.path.join(redRRoot,'libraries',package,'qtWidgets','*.py'))
    try:
        if '__init__.py' not in qtwidgets:
            f = open(os.path.join(docRoot,'libraries',package,'qtWidgets','__init__.py'),'w')
            f.write('')
            f.close()
    except: pass
    for n in qtwidgets:
        print '%s' % n
        (name,ext) = os.path.splitext(os.path.basename(n))
        if name =='__init__': continue
        #if ext != '.py': continue
        
        output = """%s
=================================
   
.. automodule:: libraries.%s.qtWidgets.%s
   :members:
   :undoc-members:
   :show-inheritance:
   
.. image:: %s.png
""" % (name,package,name,name)
            
        f = open(os.path.join(docRoot,'libraries',package,'qtWidgets',name+'.rst'),'w')
        f.write(output)
        f.close()
        if makeDeps == 1:
            cmd = graphCmd % (n,os.path.join(docRoot,'libraries',package,'qtWidgets',name))
            os.system(cmd)
###############################################
    signalClasses = glob.glob(os.path.join(redRRoot,'libraries',package,'signalClasses','*.py'))
    try:
        if '__init__.py' not in signalClasses:
            print 'Creating init for %s.widgets' % package
            f = open(os.path.join(docRoot,'libraries',package,'signalClasses','__init__.py'),'w')
            f.write('')
            f.close()
    except:
        pass
    for n in signalClasses:
        print '%s' % n
        (name,ext) = os.path.splitext(os.path.basename(n))
        if name =='__init__': continue
        #if ext != '.py': continue
        output = """%s
=================================
   
.. automodule:: libraries.%s.signalClasses.%s
   :members:
   :undoc-members:
   :show-inheritance:
   
.. image:: %s.png
""" % (name,package,name,name)
            
        f = open(os.path.join(docRoot,'libraries',package,'signalClasses',name+'.rst'),'w')
        f.write(output)
        f.close()
        if makeDeps == 1:
            cmd = graphCmd % (n,os.path.join(docRoot,'libraries',package,'signalClasses',name))
            os.system(cmd)

##################################################        
shutil.rmtree(os.path.join(os.path.abspath(docRoot),'_build'),True)
cmd = os.path.join(os.path.abspath(docRoot),'make.bat') + ' html'
print 'Running doc compiler: ' + cmd
p = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
print p

