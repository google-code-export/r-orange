import sys,re,glob
import pprint

#print sys.argv[1]
widgets = glob.glob(sys.argv[1]) 
#print widgets
for n in widgets:
    print '%s' % n
    outputs = inputs = []
    code = open(n,'r').read()
        
    input = re.search(r'self.inputs.addInput\((.*)\)',code)
    if input:
        if re.search(r'\[(.*)\]',input.group(1)):
            newstr = re.sub(r'\[(.*)\]','',input.group(1))
            (signalID,signalName,signalClass,func) = newstr.split(',')
        else:
            (signalID,signalName,signalClass,func) = input.group(1).split(',')
        print input.group(1)
        print signalID
        signalID = re.search(r"""('|")?(.*)('|")?""",signalID.strip()).group(2)
        signalName = re.search(r"""('|")?(.*)('|")?""",signalName.strip()).group(2)
        signalClass = signalClass.strip()
        inputs.append({'signalID':signalID, 'signalName':signalName,'signalClass':signalClass})

    out = re.search(r'self.outputs.addOutput\((.*)\)',code)
    if out:
        (signalID,signalName,signalClass) = out.group(1).split(',')
        outputs.append({'signalID':signalID, 'signalName':signalName,'signalClass':signalClass})
        
    
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(inputs)
    pp.pprint(outputs)
    
