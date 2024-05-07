import os

appdir = os.path.abspath(os.path.dirname(__file__))
print(appdir)
basedir = os.path.abspath(os.path.join(appdir, os.pardir))
print(basedir)