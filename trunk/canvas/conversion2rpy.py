## rpy2 conversion systems for converting rpy2 Robjects to python objects like dicts and lists
import rpy2.rpy_classic as rpy
import rpy2.robjects as ro
import numpy as np
as_character = ro.r['as.character'] ## the R function for character conversion 
as_vector = ro.r['as.vector']
def rdf2dict(rdf):  ## takes an R data frame and returns a python dict
    res = {}
    for name in rdf.names:
        vec = rdf.r[name][0]
        if vec.rclass == 'numeric':
            res[name] = [x for x in vec]
        else:
            print vec.rclass
            res[name] = [x for x in as_character(vec)]
            
    return res
    
def rvec2list(rvec):
    res = [x for x in rvec]
    return res
    
def rmat2array(rmat): # converts an RMatrix to an array
    dims = [x for x in rmat.dim] ## get the dimentions of the array, row, col
    vecrep = rvec2list(as_vector(rmat)) ## must convert to vector so that string and numeric containing R objects are treated the same
    rmat2 = []
    for j in range(dims[1]):
        liste = vecrep[(dims[0]*j):(dims[0]*(j+1))]
        rmat2.append(liste)
    res = np.array(rmat2)
    return res
    