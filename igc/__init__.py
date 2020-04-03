import sys
from . import vali
try:
    if getattr(sys, 'frozen', False):
        raise ImportError("Won't import private module in compiled application")

    from ._private import save
    print("Imported private IGC signing source successfully")

except ImportError as e:
    # print(e)  # debug
    print("Import IGC signing from shared object")
    from . import save
