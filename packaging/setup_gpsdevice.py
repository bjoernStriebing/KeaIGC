import os
from distutils.core import setup
from Cython.Build import cythonize

os.environ['CFLAGS'] = '-g0 -O3'
sourcefiles = ['gpsdevice/gpsmisc.py',
               'gpsdevice/gpsbase.py',
               'gpsdevice/gpsflymaster.py']
setup(
    ext_modules=cythonize(sourcefiles,
                          build_dir="build",
                          compiler_directives={'emit_code_comments': False,
                                               'unraisable_tracebacks': False})
)
