import rpy3.rpy_classic as rpy
rpy.set_default_mode(rpy.BASIC_CONVERSION)
a = rpy.r('1') 

a.as_py()