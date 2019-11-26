import sys
import vali
try:
    if getattr(sys, 'frozen', False):
        raise ImportError("Won't import private module in compiled application")

    import private.save as save
    print "Imported private IGC signing source successfully"

except ImportError:
    print "Import IGC signing from shared object"
    import save as save

# TODO remove save.so from gitignore
#      just don't commit binary undergoing many chanes for now.
