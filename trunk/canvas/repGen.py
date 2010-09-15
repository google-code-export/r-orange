## docutils interface.  this interface should provide some utility in making reports such as addition of figures, text, etc.

def setImage(fileDir, imageFile):
    text = 'The following plot was generated:\n\n'
    text += '.. image:: '+fileDir+'/'+str(imageFile)+'\n    :scale: 50%%\n\n'
    
    return text
    
def setParagraph(text): # sets the text of a paragraph
    return '\n\n'+text+'\n\n'
    
def setHeader(header):
    nt = '\n\n'
    nt += ')'*len(header)
    nt += header
    nt += ')'*len(header)
    nt += '\n\n'
    return nt
    
def setBreak():
    nt = '\n\n'
    nt += '>>>>>>>>>>>>>>>>>>>>>>>>'
    nt += '\n\n'
    
    return nt
    
def setTable(file, title = 'Table'):
    nt = '\n\n'
    nt += '.. csv-table:: '+str(title)+'\n  :file: '+str(file)+'\n\n'
    
    return nt
    
def setBullet(text):
    nt = '\n\n'
    nt += '-'+str(text)
    nt += '\n\n'
    
    return nt
    
def generateList(someList): 
    if type(someList) == str:
        someList = [someList]
        
    nt = '\n\n'
    for i in someList:
        nt += '-'+str(i)+'\n\n'
        
    return nt
    
def publishReport(name, text):
    from docutils.core import publish_string
    import os
    if os.path.splitext(str(name))[1].lower() in [".odt"]:#, ".html", ".tex"]
        from docutils.writers.odf_odt import Writer, Reader
        reader = Reader()
        writer = Writer()
        output = publish_string(str(text), reader = reader, writer = writer)
        file = open(name, 'wb')
        file.write(output)
        file.close()
    elif os.path.splitext(str(name))[1].lower() in [".tex"]:# , ".tex"]
        output = publish_string(str(text), writer_name='latex')#, writer = writer, reader = reader)

        file = open(name, 'w')
        file.write(output)
        file.close()

    elif os.path.splitext(str(name))[1].lower() in [".html"]:# , ".tex"]
        
        output = publish_string(str(text), writer_name='html')
        print output
        print type(output)
        print str(output)
        file = open(name, 'w')
        file.write(output)
        file.close()