from distutils.core import setup
from Cython.Build import cythonize

sourcefiles = ['gpsdevice/gpsmisc.py',
               'gpsdevice/gpsbase.py',
               'gpsdevice/gpsflymaster.py']
setup(
    ext_modules=cythonize(sourcefiles,
                          build_dir="build")
)
