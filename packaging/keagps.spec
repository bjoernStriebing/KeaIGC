# -*- coding: utf-8 -*-
# -*- mode: python -*-
# from kivy.tools.packaging.pyinstaller_hooks import get_deps_all

block_cipher = None


# dependencies = get_deps_all()

a = Analysis(['../keagps.py'],
             pathex=['../library/aerofiles'],
             binaries=[],
             datas=[],
             hiddenimports=['Crypto.Cipher.Blowfish', 'library', 'aerofiles'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['igc.private'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
# **dependencies)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          # [],
          exclude_binaries=True,
          name='keagps',
          debug=True,
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
               name='keagps')
