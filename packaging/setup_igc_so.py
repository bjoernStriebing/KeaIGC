import os
from distutils.core import setup
from Cython.Build import cythonize

os.environ['CFLAGS'] = '-g0 -O3'
sourcefiles = ["igc/_private/save.py"]
try:
    setup(
        ext_modules=cythonize(sourcefiles,
                              build_dir="build",
                              compiler_directives={'emit_code_comments': False,
                                                   'unraisable_tracebacks': False})
    )
except Exception as e:
    print("'igc/save.so' not updated due to build errors.")
    print("Most likely you don't have the source for it")
    print("We will continue to build with the prebuild 'igc/save.so'\n")
    exit(-1)
else:
    print("\n'igc/save.so' was rebuild from sources")
    print("You should consider pushing it to remote to sync with other developers\n")
    exit(0)
