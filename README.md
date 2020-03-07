# Kea GPS Downloader

A simple and intuitive interface to download .igc files from your flight recorder to PC.
Open source - if you have an instrument which is currently not supported I invite you to add to this project. ***Note: that is anything that isn't a Flymaster at the moment, sorry!***

#### Available for
- [x] Mac OSX
- [ ] Linux
- [ ] Windows

#### Screenshots
*TBC*

#### Installing
*Simple disk image with app will be available shortly*


## OSX Developer Setup Guide

1. Install `python2.7` via homebrew and make sure it's added to your path
1. `python -m pip install --upgrade pip`
1. `python -m virtualenv --no-site-packages venv`
1. `. venv/bin/activate`
1. `pip install -r requirements_osx.txt`

#### Start python app
* List all flights: `./dist/test_flymaster /dev/<tty.portname>`
* Download flight from list: `./test_flymaster /dev/<tty.portname> <number>`

#### Building the app
Simply run `./packaging/build.sh [--so] [--dmg]`. This will do the following:
* setup `PYTHONPATH` for building and clean any old outputs
* compile and sign gps device `*.pyc` files to enable tracklog authentication
* if `--so` argument is provided: compile private `igc/save.py` sources into shared library
* compile the rest of the app
* if `--dmg` argument is provided: create installer image

*Note: New or modified GPS classes require a private key signature. You can still compile and test your changes with the private key but any IGC files downloaded won't have the G-Record required to validate flights. When merging in your pull requests I will review your code and sign the GPS device library compiled from it. This may seem inconvenient but is necessary to ensure tracklogs can not be manipulated and signed with Kea GPS Downloader key*


## Windows Developer Setup Guide


#### vali-xea.exe 32 bit Developer Setup

The following assumes a parallel install of 32 bit python alongside existing 64 bit version
1. Download `python2.7.x.msi` installer (32bit)
1. Install to custom path: e.g. `C:\python2.7_32` while also selecting option to add python to your system path
1. Rename `C:\python2.7_32\python.exe` to discern from 64 bit python: e.g. `C:\python2.7_32\python_32.exe`
1. Open cmd
1. Upgrade pip: `python_32 -m pip install --upgrade pip`
1. Install virtualenv: `python_32 -m pip install virtualenv`
1. Change into this project folder
1. Create virtualenv: `python_32 -m virtualenv --no-site-packages venv`
1. Activate virtualenv: `venv\Scripts\activate`
1. Install dependencies: `pip install -r requirements_vali.txt`

###### Building vali-xea.exe
1. `pyinstaller --onefile vali.spec`
1. Executable should be in `dist\vali-xea.exe`
