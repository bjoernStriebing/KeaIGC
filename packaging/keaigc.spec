# -*- coding: utf-8 -*-
# -*- mode: python -*-
# from kivy.tools.packaging.pyinstaller_hooks import get_deps_all

block_cipher = None

# dependencies = get_deps_all()

a = Analysis(['keaigc.py'],
             pathex=['library/aerofiles'],
             binaries=[('gpsdevice/lib/gpsbase.cpython-37m-darwin.so', 'gpsdevice/lib' ),
                       ('gpsdevice/lib/gpsmisc.cpython-37m-darwin.so', 'gpsdevice/lib' ),
                       ('gpsdevice/lib/gpsflymaster.cpython-37m-darwin.so', 'gpsdevice/lib' )],
             datas=[('gpsdevice/lib/gpsbase.cpython-37m-darwin.sig', 'gpsdevice/lib' ),
                    ('gpsdevice/lib/gpsmisc.cpython-37m-darwin.sig', 'gpsdevice/lib' ),
                    ('gpsdevice/lib/gpsflymaster.cpython-37m-darwin.sig', 'gpsdevice/lib' ),
                    ('gui/img', 'gui/img'),
                    ('gui/contrib/gardenmapview/mapview/icons',
                        'gui/contrib/gardenmapview/mapview/icons')],
             # hiddenimports=['Crypto.Cipher.Blowfish', 'library', 'aerofiles',
             #                'pkg_resources.py2_warn'],
             hiddenimports=[#'library', 'aerofiles',
                            'pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['igc._private'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
# **dependencies)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='keaigc',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               # upx_exclude=[],
               name='keaigc')

app = BUNDLE(coll,
             name='Kea IGC Forager.app',
             icon='packaging/app_icon.icns',
             bundle_identifier=None,
             info_plist={'CFBundleShortVersionString': '0.0.0',
                         'NSHighResolutionCapable': 'True'})
