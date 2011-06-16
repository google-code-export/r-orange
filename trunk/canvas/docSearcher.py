"""Whoosh searcher.

This module allows red-R to search and index help documentaiton from within Red-R.  This allows us to build and use help documentaiton entirely from within the program without having to make sphinx index these files each time help is run, representing a big savings of time.  All we really need to do is to index the files and build them new each time."""

import redREnviron
import os, sys

from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser

indexDir = os.path.join(redREnviron.directoryNames['redRDir'], 'doc', 'helpIndex')
pachageHelpTemplate = 'libraries/%s/help'
coreHelpTemplate = 'doc'

def createIndex():
    if os.path.exists(indexDir):
        import shutil
        shutil.rmtree(indexDir)
    if not os.path.exists(indexDir):
        os.mkdir(indexDir)
    schema = Schema(title=TEXT(stored = True), path = ID(stored=True, unique = True), content = TEXT)
    ix = create_in(indexDir, schema)
    writer = ix.writer()
    import glob
    
    # record the core documentation
    for r in glob.glob(os.path.join(redREnviron.directoryNames['redRDir'], coreHelpTemplate, '*', '*.rst')):
        print 'indexing %s' % r
        with open(r, 'r') as f:
            writer.add_document(title = unicode(os.path.split(r)[1]), path = unicode(r).replace('.rst', '.html'), content = unicode(f.read())) 
        
    # record the package documetation
    for r in glob.glob(os.path.join(redREnviron.directoryNames['libraryDir'], '*', 'help', '*', '.rst')):
        print 'indexing %s' % r
        with open(r, 'r') as f:
            writer.add_document(title = unicode(os.path.split(r)[1]), path = unicode(r).replace('.rst', '.html'), content = unicode(f.read())) 
    writer.commit()
    
def searchIndex(term):
    """Searches for the term in the indexes and returns a list of matches.  The list will contain a dict with items 'title' and 'path'."""
    ix = open_dir(indexDir)
    with ix.searcher() as searcher:
        q = QueryParser("content", ix.schema).parse(term)
        r = searcher.search(q, limit = 50)
        res = []
        for re in r:
            res.append({'title':re['title'], 'path':re['path']})
            
    return res
    