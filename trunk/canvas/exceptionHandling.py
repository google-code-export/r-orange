import sys, traceback,os
from datetime import tzinfo, timedelta, datetime


def getSafeString( s):
    return str(s).replace("<", "&lt;").replace(">", "&gt;")

def formatException(type=None, value=None, tracebackInfo=None):
    if not tracebackInfo:
        (type,value, tracebackInfo) =  sys.exc_info()
        
    t = datetime.today().isoformat(' ')
    text =  '<br>'*2 + '#'*60 + '<br>\n'
    
    text += "Unhandled exception of type %s occured at %s:<br>Traceback:<br>\n" % ( getSafeString(type.__name__), t)
    list = traceback.extract_tb(tracebackInfo, 10)
    #print list
    space = "&nbsp; "
    totalSpace = space
    #print range(len(list))
    for i in range(len(list)):
        # print list[i]
        (file, line, funct, code) = list[i]
        #print 'code', code
        
        (dir, filename) = os.path.split(file)
        text += "" + totalSpace + "File: <b>" + filename + "</b>, line %4d" %(line) + " in <b>%s</b><br>\n" % (getSafeString(funct))
        if code != None:
            code = code.replace('<', '&lt;') #convert for html
            code = code.replace('>', '&gt;')
            code = code.replace("\t", "\x5ct") # convert \t to unicode \t
            text += "" + totalSpace + "Code: " + code + "<br>\n"
        totalSpace += space
    
    lines = traceback.format_exception_only(type, value)
    for line in lines[:-1]:
        text += "" + totalSpace + getSafeString(line) + "<br>\n"
    text += "<b>" + totalSpace + getSafeString(lines[-1]) + "</b><br>\n"
    text +=  '#'*60 + '<br>'*2
    return text

