from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("igc/private/save.py",
                          build_dir="build")
)
