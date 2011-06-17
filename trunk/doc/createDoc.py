graphCmd = 'python dep.py %s | dot -T png -o %s.png'

import sys,os,glob,subprocess
import shutil

redRRoot = sys.argv[1]
docRoot = os.path.join(redRRoot, 'doc')
sys.path.append(os.path.join(redRRoot, 'canvas'))
makeDeps = False #int(sys.argv[2])

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
    
packageList = []
for p in glob.glob(os.path.join(redRRoot, 'libraries', '*', 'package.xml')):
    try:
        cmd = 'python %s %s' % (os.path.join(redRRoot, 'doc', 'createPackageDoc.py'), os.path.split(p)[0])
        print cmd
        pro = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell = True).communicate()[0]
        print pro
        packageList.append(os.path.join(os.path.split(os.path.split(p)[0])[1], 'help'))
        shutil.copytree(os.path.join(os.path.split(p)[0], 'help'), os.path.join(docRoot,'libraries', os.path.split(os.path.split(p)[0])[1], 'help'), ignore = shutil.ignore_patterns('*.svn', '*.svn*'))
    except Exception as inst:
        print 'Error in making docs for %s %s' % (p, str(inst))
        
# userdoc = """Users's documentation!
# =================================

# This is the main source for general Red-R and Package help documentation.  Feel free to also post comments on the forum, send emails, or follow us on Twitter!!

   
# Red-R Packages:

# .. toctree::
   # :glob:
   # :maxdepth: 1
    
# %s""" % '\n'.join(['   %s' % os.path.join(p, 'userDoc', 'index').replace('\\', '/') for p in packageList])
# with open(os.path.join(docRoot,'userDoc.rst'),'w') as f:
    # f.write(userdoc)
    
# devdoc = """Developer's documentation!
# =================================

# This documentation is designed for developers.  The documentation is highly technical, while it is actually quite interesting if you want to know how Red-R is working, the documentation might not be what general users are looking for.  If you think you are here by mistake you should go to the main table of contents and look at the user documentation.

# Contents:

# .. toctree::
   # :glob:
   # :maxdepth: 2
    
   # intro
   # core
   
# Red-R Packages:

# .. toctree::
   # :glob:
   # :maxdepth: 1
    
# %s""" % '\n'.join(['   %s' % os.path.join(p, 'devDoc', 'index').replace('\\', '/') for p in packageList])
# with open(os.path.join(docRoot,'devDocs.rst'),'w') as f:
    # f.write(devdoc)
    
   
   #########################################################################


    
# packages = glob.glob(os.path.join(redRRoot,'libraries','base','package.xml'))
# if not os.path.exists(os.path.join(docRoot, 'libraries')): os.mkdir(os.path.join(docRoot, 'libraries'))

# for p in packages:
    # package = os.path.split(os.path.split(p)[0])[1]
    # if not os.path.exists(os.path.join(docRoot,'libraries',package)):
        # os.mkdir(os.path.join(docRoot,'libraries',package))
        # os.mkdir(os.path.join(docRoot,'libraries',package,'widgets'))
        # os.mkdir(os.path.join(docRoot,'libraries',package,'qtWidgets'))
        # os.mkdir(os.path.join(docRoot,'libraries',package,'signalClasses'))
    # with open(os.path.join(redRRoot, 'libraries', package, 'package.xml'), 'r') as f:
        # xml = f.read()
        
    # libraryOut = """%(PACKAGENAME)s Package
# =================================
# Contents
# ~~~~~~~~

# Widgets:

# .. toctree::
   # :glob:
   # :maxdepth: 2
   
   # widgets/*
   
# QT Widgets:

# .. toctree::
   # :glob:
   # :maxdepth: 2
   
   # qtWidgets/*

# Signal Classes:

# .. toctree::
   # :glob:
   # :maxdepth: 2
   
   # signalClasses/*
# """ % {'PACKAGENAME':package, 'PACKAGEXML':xml}
    # f = open(os.path.join(docRoot,'libraries',package,package+'.rst'),'w')
    # f.write(libraryOut)
    # f.close()
    
############################################    
    # widgets = glob.glob(os.path.join(redRRoot,'libraries',package,'widgets','*.py'))
    # try:
        # if '__init__.py' not in widgets:
            # f = open(os.path.join(docRoot,'libraries',package,'widgets','__init__.py'),'w')
            # f.write('')
            # f.close()
    # except: pass
    # for n in widgets:
        # print '%s' % n
        # (name,ext) = os.path.splitext(os.path.basename(n))
        # if name =='__init__': continue
        # with open(os.path.join(redRRoot, 'libraries', package, 'meta', 'widgets', name + '.xml'), 'r') as f:
            # xml = f.read()
        # output = """%(WIDGETNAME)s
# =================================
   
# .. automodule:: libraries.%(PACKAGENAME)s.widgets.%(WIDGETNAME)s
   # :members:
   # :undoc-members:
   # :show-inheritance:
   
# """ % {'WIDGETNAME':name, 'PACKAGENAME':package, 'WIDGETXML':xml}
        # if makeDeps == 1:
            # output += """
# .. image:: %s.png
# """ % name

            
        # f = open(os.path.join(docRoot,'libraries',package,'widgets',name+'.rst'),'w')
        # f.write(output)
        # f.close()
        
        # if makeDeps == 1:
            # cmd = graphCmd % (n,os.path.join(docRoot,'libraries',package,'widgets',name))
            # os.system(cmd)
############################################
    # qtwidgets = glob.glob(os.path.join(redRRoot,'libraries',package,'qtWidgets','*.py'))
    # try:
        # if '__init__.py' not in qtwidgets:
            # f = open(os.path.join(docRoot,'libraries',package,'qtWidgets','__init__.py'),'w')
            # f.write('')
            # f.close()
    # except: pass
    # for n in qtwidgets:
        # print '%s' % n
        # (name,ext) = os.path.splitext(os.path.basename(n))
        # if name =='__init__': continue
        ##if ext != '.py': continue
        
        # output = """%(WIDGETNAME)s
# =================================
   
# .. automodule:: libraries.%(PACKAGENAME)s.qtWidgets.%(WIDGETNAME)s
   # :members:
   # :undoc-members:
   # :show-inheritance:
   
# """ % {'WIDGETNAME':name, 'PACKAGENAME':package}
        # if makeDeps == 1:
            # output += """
# .. image:: %s.png
# """ % name
            
        # f = open(os.path.join(docRoot,'libraries',package,'qtWidgets',name+'.rst'),'w')
        # f.write(output)
        # f.close()
        # if makeDeps == 1:
            # cmd = graphCmd % (n,os.path.join(docRoot,'libraries',package,'qtWidgets',name))
            # os.system(cmd)
############################################
    # signalClasses = glob.glob(os.path.join(redRRoot,'libraries',package,'signalClasses','*.py'))
    # try:
        # if '__init__.py' not in signalClasses:
            # print 'Creating init for %s.widgets' % package
            # f = open(os.path.join(docRoot,'libraries',package,'signalClasses','__init__.py'),'w')
            # f.write('')
            # f.close()
    # except:
        # pass
    # for n in signalClasses:
        # print '%s' % n
        # (name,ext) = os.path.splitext(os.path.basename(n))
        # if name =='__init__': continue
        ##if ext != '.py': continue
        # output = """%(WIDGETNAME)s
# =================================
   
# .. automodule:: libraries.%(PACKAGENAME)s.signalClasses.%(WIDGETNAME)s
   # :members:
   # :undoc-members:
   # :show-inheritance:
   
# """ % {'WIDGETNAME':name, 'PACKAGENAME':package}
        # if makeDeps == 1:
            # output += """
# .. image:: %s.png
# """ % name
            
        # f = open(os.path.join(docRoot,'libraries',package,'signalClasses',name+'.rst'),'w')
        # f.write(output)
        # f.close()
        # if makeDeps == 1:
            # cmd = graphCmd % (n,os.path.join(docRoot,'libraries',package,'signalClasses',name))
            # os.system(cmd)

#################################################        
shutil.rmtree(os.path.join(os.path.abspath(docRoot),'_build'),True)
cmd = 'sphinx-build -b html %s %s' % (os.path.abspath(docRoot), os.path.join(os.path.abspath(docRoot),'_build'))
print 'Running doc compiler: ' + cmd
p = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
print p

import docSearcher
docSearcher.createIndex()
