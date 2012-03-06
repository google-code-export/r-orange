#graphCmd = 'python dep.py %s | dot -T png -o %s.png'

import sys,os,glob,subprocess
import shutil
print os.path.abspath(sys.argv[0])
try:
    sys.path.append(os.path.split(os.path.abspath(sys.argv[0])))
    import createPackageDoc
    print 'Imported createPackageDoc from local directory'
except Exception as inst:
    print str(inst)
    import doc.createPackageDoc as createPackageDoc

#redRRoot = sys.argv[1]

def makeDoc(redRRoot, makeCore = False):
    
    docRoot = os.path.join(redRRoot, 'doc')
    sys.path.append(os.path.join(redRRoot, 'canvas'))

    # toRM = glob.glob(os.path.join(docRoot,'core','*.rst')) + glob.glob(os.path.join(docRoot,'libraries','*','*','*.rst')) + glob.glob(os.path.join(docRoot,'libraries','*','*.rst')) + glob.glob(os.path.join(docRoot,'libraries','*.rst'))

    # for x in toRM: os.remove(x)
    if makeCore:
        shutil.rmtree(os.path.join(docRoot,'core'),True)
        os.mkdir(os.path.join(docRoot,'core'))
        
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
            # if makeDeps == 1:
                # output += """
    # .. image:: %s.png
    # """ % name
                # cmd = graphCmd % (n,os.path.join(docRoot,'core',name))
                # print cmd
                # os.system(cmd)
            #print output
            f = open(os.path.join(docRoot,'core',name+'.rst'),'w')
            f.write(output)
            f.close()
            
    shutil.rmtree(os.path.join(docRoot,'libraries'),True)
    os.mkdir(os.path.join(docRoot,'libraries'))

    #packageList = []
    for p in glob.glob(os.path.join(redRRoot, 'libraries', '*', 'package.xml')):
        try:
            createPackageDoc.createDoc(os.path.split(p)[0])
            
            #packageList.append(os.path.join(os.path.split(os.path.split(p)[0])[1], 'help')) # ex; base/help
            #shutil.copytree(os.path.join(os.path.split(p)[0], 'help'), os.path.join(docRoot,'libraries', os.path.split(os.path.split(p)[0])[1], 'help'), ignore = shutil.ignore_patterns('*.svn', '*.svn*'))
        except Exception as inst:
            print 'Error in making docs for %s %s' % (p, str(inst))
    
    #print 'Generated documentation for packages %s' % unicode(packageList)
    
    #################################################        
    shutil.rmtree(os.path.join(os.path.abspath(docRoot),'_build'),True)
    cmd = 'sphinx-build -b html %s %s' % (os.path.abspath(docRoot), os.path.join(os.path.abspath(docRoot),'_build'))
    print 'Running doc compiler: ' + cmd
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True, cwd=os.path.join(redRRoot, 'doc')).communicate()[0]
    print p

    #import docSearcher
    #docSearcher.createIndex(redRRoot)
    
if sys.argv[1]:
    print 'Found sys.argv[1] to be %s' % sys.argv[1]
    makeDoc(sys.argv[1], True)
