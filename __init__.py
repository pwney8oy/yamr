from yamr.base import *
from yamr.builders import *
from yamr.extras import *
import os, sys

__all__ = ['Builder', 'CCompiler', 'Compile', 'DataFile', 'DoCommand', 'DoCopy', 'DoMakeDir',
'DoMove', 'DoRemove', 'DoRemoveDir', 'DoRemoveFile', 'DoRemoveTree', 'Executable', 'ExecuteCommand',
'Export', 'File', 'Glob', 'GlobDict', 'GlobDictRec', 'GlobTree', 'MkDir', 'NoDepend',
'SetupYAMR', 'SharedLibrary', 'StaticLibrary', 'Token']

def SetupYAMR():
    if os.path.split(sys.argv[0])[0]:
        os.chdir(os.path.split(sys.argv[0])[0])

    if not os.path.exists("yamrbuild"):
        os.mkdir("yamrbuild")
