# Alternative versions of common shell commands that print themselves
# as they are performed

import os, shutil, sys

bit = '-'

def DoCommand(command):
    print bit, command
    result = os.system(command)
    if result!=0:
        print "[YAMR: %s failed: %d]" % (command, result)
        sys.exit(1)

def DoMove(src, dest):
    print bit, "move", src, dest
    shutil.move(src, dest)

def DoCopy(src, dest):
    print bit, "copy", src, dest
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    else:
        shutil.copy(src, dest)

def DoMakeDir(name):
    print bit, "mkdir", name
    os.mkdir(name)

def DoRemove(name):
    print bit, "remove", name
    if os.path.isdir(name):
        shutil.rmtree(name)
    else:
        os.remove(name)

def DoRemoveFile(name):
    print bit, "remove-file", name
    os.remove(name)

def DoRemoveDir(name):
    print bit, "remove-dir", name
    os.rmdir(name)

def DoRemoveTree(name):
    print bit, "remove-dir-tree", name
    shutil.rmtree(name)
