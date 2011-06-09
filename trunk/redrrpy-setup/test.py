import rpy2.robjects as ro
import _conversion as co
import time
## inital test of Rpy2 conversion
rpy2time = {}
for i in ['1000', '10000', '50000', '100000', '500000']:
    rpy2time[i] = []
    test = ro.r('test<-matrix(rnorm(%s), ncol = 100)' % i)
    for j in range(100):
        t1 = time.time() # get clock time 1
        temp = ro.r('test') # convert test to rpy2 RObject, set temp to supress printing output
        t2 = time.time() # get clock time 2
        rpy2time[i].append(t2-t1)
for i, j in rpy2time.items():
    print 'Average conversion time for %s elements is: %s' % (str(i), str(sum(j)/len(j)))
coTime = {}
for i in ['1000', '10000', '50000', '100000', '500000']:
    coTime[i] = []
    test = ro.r('matrix(rnorm(%s), ncol = 100)' % i)
    for j in range(100):
        t1 = time.time() # get time 1
        temp = co.convert(test) # convert, set temp to supress printing output
        t2 = time.time() # get time 2
        coTime[i].append(t2-t1)
for i, j in coTime.items():
    print 'Average conversion time for %s elements is: %s' % (str(i), str(sum(j)/len(j)))
## do not run
ro.r('rpy2Data<-list()')
for i in ['1000', '10000', '50000', '100000', '500000']:
    ro.r('rpy2Data[[\"%s\"]] <- c(%s)' % (i, ','.join(str(j) for j in rpy2time[i])))
    
ro.r('jpeg("C:/users/covingto/rpy2Data.jpg")')
ro.r('boxplot(rpy2Data, xlab = "Matrix Size", ylab = "Time (s)")')
ro.r('dev.off()')
ro.r('coData<-list()')
for i in ['1000', '10000', '50000', '100000', '500000']:
    ro.r('coData[[\"%s\"]] <- c(%s)' % (i, ','.join(str(j) for j in coTime[i])))
ro.r('jpeg("C:/users/covingto/coData.jpg")')
ro.r('boxplot(coData, xlab = "Matrix Size", ylab = "Time (s)")')
ro.r('dev.off()')
## end do not run

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

iris = co.convert(ro.r('iris'))
iris2 = {}
for n in iris.keys():
    if n == 'Species': continue
    iris2[n] = iris[n]
def dictBoxplot(d, ymax, ymin, label):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    pos = np.array(range(len(d.keys())))
    bp = ax.boxplot(d.values(), sym = 'k+', notch = 1)
    ax.set_xticklabels(d.keys())
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(label)
    plt.show()
dictBoxplot(iris2, 0, 8, 'Length')
ro.r('irisSplit<-split(iris, iris$Species)')
    
irisSetosa = {}
for n in iris.keys():
    if n == 'Species': continue
    irisSetosa[n] = co.convert(ro.r('irisSplit$setosa'))[n]
    
dictBoxplot(irisSetosa, 8, 0, 'Length')

irisVersicolor = {}
for n in iris.keys():
    if n == 'Species': continue
    irisVersicolor[n] = co.convert(ro.r('irisSplit$versicolor'))[n]
dictBoxplot(irisVersicolor, 8, 0, 'Length')
    
irisVirginica = {}
for n in iris.keys():
    if n == 'Species': continue
    irisVirginica[n] = co.convert(ro.r('irisSplit$virginica'))[n]
dictBoxplot(irisVirginica, 8, 0, 'Length')
    
    
    
    
names = co.convert(ro.r('levels(iris$Species)'))

batchMeans = {}
for n in names:
    batchMeans[n] = co.convert(ro.r('lapply(irisSplit$%s, mean)' % n))
batchStdError = {}
for n in names:
    batchStdError[n] = co.convert(ro.r('lapply(irisSplit$%s, sd)' % n))
    
means = []
for n in names:
    for m in batchMeans[n].keys():
        if m == 'Species': continue
        means.append(batchMeans[n][m])
sds = []
for n in names:
    for m in batchStdError[n].keys():
        if m == 'Species': continue
        sds.append(batchStdError[n][m])
## start the figure
fig = plt.figure()
ax = fig.add_subplot(111)
width = 0.2
ind = np.arange(4)
rects1 = ax.bar(ind, means[0:4], width, color = 'r', yerr = sds[0:4])
rects2 = ax.bar(ind+width, means[4:8], width, color = 'b', yerr = sds[4:8])
rects3 = ax.bar(ind+width+width, means[8:12], width, color = 'g', yerr = sds[8:12])
ax.set_ylabel('Length')
ax.set_xticks(ind+width*1.5)
ax.set_xticklabels(('Petal Length', 'Sepal Length', 'Petal Width', 'Sepal Width'))
ax.legend((rects1[0], rects2[0], rects3[0]), names)
plt.show()
