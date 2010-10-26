from distutils.core import setup, Extension
import os
RHOME = 'C:/Program Files/R/R-2.9.2/'
include_dirs = [ os.path.join(RHOME.strip(), 'include'),
                         'src' ]
libraries= ['R']
r_libs = [ # Different verisons of R put .so/.dll in different places
              os.path.join(RHOME, 'bin'),  # R 2.0.0+
              os.path.join(RHOME, 'lib'),  # Pre 2.0.0
             ]
library_dirs = r_libs
        
        
module1 = Extension('_conversion',
                    sources = ['src/conversion.c']
                    ,
                    include_dirs=include_dirs,
                    libraries=libraries,
                    library_dirs=library_dirs)
setup (name = 'KyleTest',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])