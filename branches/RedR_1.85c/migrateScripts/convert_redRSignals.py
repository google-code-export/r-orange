import re, sys, os.path, glob

test = sys.argv[2]

def getSignalList(regex, data):
    inmo = regex.search(data)
    if inmo:
        return str([tuple([y[0] in "'\"" and y[1:-1] or str(y) for y in (x.strip() for x in ttext.group(1).split(","))])
               for ttext in re_tuple.finditer(inmo.group("signals"))])
    else:
        return "[]"


re_inputs = re.compile(r'[ \t]+self.inputs\s*=\s*(?P<signals>\[[^]]*\])', re.DOTALL)
re_outputs = re.compile(r'[ \t]+self.outputs\s*=\s*(?P<signals>\[[^]]*\])', re.DOTALL)
re_tuple = re.compile(r"\(([^)]+)\)")


if os.path.isdir(sys.argv[1]):
    files = glob.glob(sys.argv[1]+'/*.py')
else:
    files = [sys.argv[1]]

for n in files:
    print '\n\n####################%s######################\n\n' % n
    data = open(n,'r').read()

    inputs = getSignalList(re_inputs,data)
    outputs = getSignalList(re_outputs,data)
    inputs = eval(inputs)
    outputs = eval(outputs)
    #print inputs
    signals = {}
    
    if inputs:
        m = re.search(r'([ \t]+)self.inputs\s*=\s*(?P<signals>\[[^]]*\])',data)
        code = ''
        for i,x in zip(range(len(inputs)),inputs): 
            #print x
            theClass = x[1].split('.')
            signals[theClass[-1]] = 1
            code += m.group(1) + "self.inputs.addInput('id%d', '%s', redR%s, %s)\n" % (i,x[0],theClass[-1],x[2])

        data = re_inputs.sub(code,data)
    if outputs:
        slots = []
        m = re.search(r'([ \t]+)self.outputs\s*=\s*(?P<signals>\[[^]]*\])', data)
        code = ''
        for i,x in zip(range(len(outputs)),outputs): 
            #print x
            theClass = x[1].split('.')
            signals[theClass[-1]] = 1
            slots.append(('id'+str(i),x[0]))
            code += m.group(1) + "self.outputs.addOutput('id%d', '%s', redR%s)\n" % (i,x[0],theClass[-1])
            #print code
        data = re_outputs.sub(code,data)
        for id,name in slots:
            print id,name
            data = re.sub('self.rSend\((\'|")%s(\'|"),' % name,'self.rSend("%s",' % id, data)

    #print signals
    for x in signals.keys():
        #m = re.search(r'import.*%s\n'% x,data)
        data= re.sub(r'import.*%s.*\n'% x,'from libraries.base.signalClasses.%s import %s as redR%s\n' % (x,x,x) ,data)
        data= re.sub(r'\w+\.%s\('% x, 'redR%s(' % (x) ,data)
        
    if test == '1':
        print data
    else:
        f = open(n,'w')
        f.write(data)
        f.close()


