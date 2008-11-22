from yamr.builders import *
import glob, os

__all__ = ["Glob", "GlobDict", "GlobTree", "GlobDictRec"]

def Glob(pattern):
    """Glob(pattern, fileclass=File) -> list of File
The Glob function produces a list of files tokens from the given pattern.
If 'fileclass' is specified, it is the builder that will be used in place
of File."""
    files = []
    for path in glob.iglob(pattern):
        files.append(File(path))
    return files

def GlobDict(pattern):
    """GlobDict(pattern, fileclass=File) -> dict of key to File
The GlobDict function is like the Glob function, but instead of creating
a list of File objects it creates a dictionary that maps names to File
objects. The name used is the last part of the path to the file."""
    files = {}
    for path in glob.iglob(pattern):
        files[os.path.split(path)[-1]] = File(path)
    return files

def GlobDictRec(root, pattern="*"):
	"""GlobDictRec(root, pattern="*", fileclass=File) -> dict of key to File
The GlobDictRec is like GlobTree except that it returns the result as a
dictionary instead of a builder."""
	d = GlobDict(os.path.join(root,pattern))
	
	for dir in os.listdir(root):
		if os.path.isdir(os.path.join(root,dir)):
			d[dir] = GlobTree(os.path.join(root,dir))
	
	return d

def GlobTree(root, pattern="*"):
	"""GlobTree(root, pattern="*", fileclass=File) -> builder
The GlobTree builder converts an entire directory tree into a builder. If
pattern is specified, then only files that match the pattern will be used."""
	d = GlobDictRec(root, pattern)
	
	return MkDir(d)