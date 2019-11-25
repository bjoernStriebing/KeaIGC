from distutils.core import setup
from Cython.Build import cythonize

try:
    setup(
        ext_modules=cythonize("igc/private/save.py",
                              build_dir="build")
    )
except Exception:
    print "'igc/save.so' not updated due to build errors."
    print "Most likely you don't have the source for it"
    print "We will continue to build with the prebuild 'igc/save.so'\n"
    exit(-1)
else:
    print "\n'igc/save.so' was rebuild from sources"
    print "You should consider pushing it to remote to sync with other developers\n"
    exit(0)
