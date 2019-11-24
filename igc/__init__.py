import vali as vali
import private.save as save
try:
    import private.save as save
    print "Imported private IGC signing source successfully"
except ImportError:
    print "Import IGC signing from shared object"
    import save as save

# TODO remove save.so from gitignore
#      just don't commit binary undergoing many chanes for now.
