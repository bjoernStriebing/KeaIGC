windows 32bit setup for vali-xea.exe

assuming parallel install of 32bit alongside existing 64 bit
1) download python2.7.x.msi installer (32bit); select adding pyhton to path
2) install to custom path: e.g. C:\python2.7_32
3) rename C:\python2.7_32\python.exe to discern from 64 bit python: e.g. c:\python2.7_32\python_32.exe
4) open cmd
5) upgrade pip: python_32 -m pip install --upgrade pip
6) install virtualenv: python_32 -m pip install virtualenv
7) change into this project folder
8) create virtualenv: python_32 -m virtualenv --no-site-packages venv
9) activate virtualenv: venv\Scripts\activate
10) install dependencies: pip install -r requirements_vali.txt
----
11) build vali win32 executable: pyinstaller --onefile vali.spec
12) executable should be in dist\vali-xea.exe