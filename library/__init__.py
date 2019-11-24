import os
import sys
aerofiles_path = os.path.join(os.path.dirname(__file__), 'aerofiles')
sys.path.append(aerofiles_path)

import aerofiles                                                        # nopep8

__all__ = ['aerofiles']
