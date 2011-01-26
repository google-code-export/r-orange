## redRi18n (internationalization)  a module to control the internationalization of Red-R, ideally this should use the _() syntax that is common to the internationalization community.

## Copywrite 2011 Kyle R Covington

import redREnviron, gettext, os, redRLog
from OrderedDict import OrderedDict
core_ = None
def superfallback(a):
    return a

def Coreget_(domain = 'messages', locale = os.path.join(redREnviron.directoryNames['redRDir'], 'languages'), languages = None, fallback = False):
    global core_
    if core_ != None:
        return core_
    else:
        try:
            if languages == None:
                try:
                    languages = redREnviron.settings['language'].keys()
                except:
                    redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
                    languages == ['en_EN.ISO8859-1']
                    core_ = superfallback
                    return core_
            if languages[0] == 'en_EN.ISO8859-1':
              core_ = superfallback
            else:
                t = gettext.translation(domain, localedir = locale, languages = languages, fallback = fallback)
                core_ = t.gettext
                return core_  # returns the function
        except Exception as inst:
            print 'Exception occured in setting the Coreget_ function, %s' % unicode(inst)
            return superfallback
        
def get_(domain = 'messages', package = 'base', languages = None, fallback = False, locale = None):
    #if locale: print locale
    try:
        if languages == None:
            try:
                languages = redREnviron.settings['language'].keys()
            except:
                print redREnviron.settings['language']
                redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
                languages = ['en_EN.ISO8859-1']
                return superfallback
        if languages[0] == 'en_EN.ISO8859-1':
            return superfallback
        file = os.path.join(redREnviron.directoryNames['libraryDir'], package, 'languages')
        #print file
        t = gettext.translation(domain, localedir  = os.path.join(redREnviron.directoryNames['libraryDir'], package, 'languages'), languages = languages, fallback = fallback)
        return t.gettext  # returns the function
    except Exception as inst:
        redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
        print 'Exception occured in setting the get_ function, %s' % unicode(inst)
        return superfallback