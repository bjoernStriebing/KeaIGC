# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import biplist
import os.path

# .. Useful stuff ..............................................................
application = defines.get('app', 'dist/Kea IGC Forager.app')


def icon_from_app(app_path):
    plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
    plist = biplist.readPlist(plist_path)
    icon_name = plist['CFBundleIconFile']
    icon_root, icon_ext = os.path.splitext(icon_name)
    if not icon_ext:
        icon_ext = '.icns'
    icon_name = icon_root + icon_ext
    return os.path.join(app_path, 'Contents', 'Resources', icon_name)


# .. Basics ....................................................................
format = defines.get('format', 'UDBZ')
size = defines.get('size', None)
files = [application]
symlinks = {'Applications': '/Applications'}

# Volume icon
icon = icon_from_app(application)
icon_locations = {
    'Kea IGC Forager.app': (590, 105),
    'Applications': (590, 341),
    '.VolumeIcon.icns': (2400, 100),
    '.background.png': (2400, 100),
}

# .. Window configuration ......................................................
window_rect = ((305, 189), (800, 494))
background = 'packaging/dmg_background.png'
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
default_view = 'icon-view'

# General view configuration
show_icon_preview = False

# .. Icon view configuration ...................................................
arrange_by = None
grid_offset = (0, 0)
grid_spacing = 1
scroll_position = (0, 0)
label_pos = 'bottom'
text_size = 14
icon_size = 96

# .. License configuration .....................................................
