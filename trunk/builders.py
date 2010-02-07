from yamr.base import *
from yamr.base import mtime
from yamr.actions import *
import os, re
from datetime import datetime

class File(Builder):
	"""File(path) -> Token\n
The File builder simply produces the contents of the given source file."""

	def start(self, path):
		self.path = path
		assert os.path.exists(path), "File() called with a nonexistent path: \"%s\""%path

		self.result = Token(self, filename=path)

		self.set_intokens([])
		self.set_outtokens([self.result])
		
		return self.result

	def build(self):
		raise Exception, "File.build() should never be called."

	def identify(self):
		return self.path

	def change_time(self):
		return mtime(self.path)

class ExecuteCommand(Builder):
	"""ExecuteCommand(command, inputs=[], keyedinputs={}) -> Token
Allows for execution of an arbitrary shell command. "command" should be a format string where
"%(output)s" is the name of the file to be produced and "%(inputs)s" is a space-separated list of
input filenames to the command. "inputs" should be a list of input tokens. For example, a simple GCC
compilation command could be "ExecuteCommand('gcc %(inputs)s -o %(output)s', [File("foo.c")])".

"keyedinputs" should be a dictionary that maps command-line flags to input tokens. It does not
have very many uses."""
	def start(self, command, inputs=[], keyedinputs={}):
		self.command = command
		self.inputs = inputs
		self.keyedinputs = keyedinputs
		self.result = Token(self)

		self.set_intokens(self.inputs+self.keyedinputs.values())
		self.set_outtokens([self.result])

		return self.result

	def build(self):
		inputs = [s.complete() for s in self.inputs]
		for k,v in self.keyedinputs.iteritems():
			inputs.append(k+" "+v.complete())
		
		subs = {}
		subs["output"] = self.result.filename()
		subs["input"] = " ".join(inputs)
		
		command = self.command % subs
		DoCommand(command)
		assert os.path.exists(self.result.filename()), \
			"%s failed to produce %s." % (command, subs["output"])
		self.result.finished()

	def identify(self):
		return "ExecuteCommand(%s,%s,%s)" % \
			(self.command,
			 ",".join([s.identify() for s in self.inputs]),
			 ",".join([k+"="+s.identify() for k,s in self.keyedinputs.iteritems()]))

class CCompiler(ExecuteCommand):
	"""CCompiler(command, inputs=[], keyedinputs={}) -> Token
CCompiler is a builder that scans its input files for dependencies and automatically rebuilds
if a dependency has changed."""
	
	# "#import" is a preprocessor command used by Objective-C
	dependency_re = re.compile(r'#(?:include|import)\s+"([^"]+)"\n')
	i_flag_re = re.compile(r"-I[ ]?((?:[^ \\]+|[\\][ \\])+)")
	ipath_flag_re = re.compile(r"-ipath[ ]?((?:[^ \\]+|[\\][ \\])+)")
	# no support for GCC's "-I-" flag
	
	def change_time(self):
		# extract -I and -ipath flags from GCC command line
		searchpaths = []
		for path in self.i_flag_re.findall(self.command):
			searchpaths.append(path.replace("\\ "," "))
		for path in self.ipath_flag_re.findall(self.command):
			searchpaths.append(path.replace("\\ "," "))
		
		most_recent_change = datetime.min
		
		# search recursively through input files looking for dependencies
		queue = [i.complete() for i in self.inputs]
		checked = set()
		while queue:
			next = queue.pop()
			if next in checked:
				continue
			checked.add(next)
			
			most_recent_change = max(most_recent_change, mtime(next))
			
			basedir = os.path.split(next)[0]
			f = file(next)
			for line in f:
				m = self.dependency_re.match(line)
				if m:
					name = m.group(1)
					
					# check directory of C source file
					if os.path.exists(os.path.join(basedir,name)):
						queue.append(os.path.join(basedir,name))
						continue
					
					# check command-line search paths
					for searchpath in searchpaths:
						if os.path.exists(os.path.join(searchpath,name)):
							queue.append(os.path.join(searchpath,name))
							break
					
					# don't bother checking system header directories...
			
			f.close()
				
		return most_recent_change

def CompileC(inputs, flags="", keyedinputs={}):
	"""CompileC(inputs, flags="", keyedinputs={}) -> Token
Compiles a group of source files into an object file using GCC. The input files will be
automatically scanned for C "#include" directives."""
	return CCompiler('gcc -c -o "%%(output)s" %%(input)s %s' % flags, inputs, keyedinputs)
Compile = CompileC

def CompileCPP(inputs, flags="", keyedinputs={}):
	"""CompileCPP(inputs, flags="", keyedinputs={}) -> Token
Compiles a group of source files into an object file using G++. The input files will automatically
be scanned for C "#include" directives."""
	return CCompiler('g++ -c -o "%%(output)s" %%(input)s %s' % flags, inputs, keyedinputs)

def Executable(inputs, flags="", keyedinputs={}):
	"""Executable(inputs, flags="", keyedinputs={}) -> Token
Compiles a group of object files into an executable using GCC."""
	# in theory, the arguments to Executable() should be object files, but in practice people will
	# pass source files. so we use CCompiler() instead of ExecuteCommand().
	return CCompiler('g++ -o "%%(output)s" %%(input)s %s' % flags, inputs, keyedinputs)

def SharedLibrary(inputs, flags="", keyedinputs={}):
	"""SharedLibrary(inputs, flags="", keyedinputs={}) -> Token
Compiles a group of object files into a shared library using GCC."""
	if sys.platform=="darwin": theflag = "-dynamiclib"
	else: theflag = "-shared"
	return CCompiler('gcc %s -o "%%(output)s" %%(input)s %s' % (theflag, flags), inputs, keyedinputs)

class StaticLibrary(Builder):
	"""StaticLibrary(inputs) -> Token
Compiles a group of object files into a static library using ar. Automatically runs ranlib on the
result."""
	def start(self, sources):
		self.sources = sources
		self.result = Token(self)

		self.set_intokens(self.sources)
		self.set_outtokens([self.result])

		return self.result

	def build(self):
		sourcefiles = " ".join(['"'+s.complete()+'"' for s in self.sources])
		
		command = "ar cr \"%s\"" % self.result.filename()
		command += " " + sourcefiles
		DoCommand(command)
		DoCommand("ranlib \"%s\"" % self.result.filename())

		self.result.finished()

	def identify(self):
		return "StaticLibrary(%s)" % ",".join([s.identify() for s in self.sources])

class MkDir(Builder):
	"""MkDir({"filename":Token, ...}) -> Token
The MkDir builder builds a directory with the given dictionary."""
	def start(self, contents):
		assert isinstance(contents, dict)
		assert all(isinstance(tok,Token) for tok in contents.values())
		assert all(isinstance(key,str) for key in contents.keys())

		self.contents = contents

		self.result = Token(self)

		self.set_intokens(self.contents.values())
		self.set_outtokens([self.result])

		return self.result

	def perform(self):
		# We override perform() instead of build() because we want custom
		# control over what gets rebuilt
		
		dirname = self.result.filename()
		if not os.path.exists(dirname):
			DoMakeDir(dirname)
		assert os.path.isdir(dirname)

		for name, token in self.contents.iteritems():
			fname = os.path.join(dirname, name)
			if not os.path.exists(fname) or \
				token.builder.change_time() > mtime(fname):
				
				if os.path.exists(fname):
					DoRemove(fname)
				DoCopy(token.complete(), fname)
		
		self.result.finished()

	def identify(self):
		bits = [k+"-"+v.identify() for k,v in self.contents.iteritems()]
		return "Mkdir(%s)" % ",".join(bits)


class DataFile(Builder):
	"""DataFile(string) -> Token
The DataFile builder writes the given string to a file and then produces that
file."""
	def start(self, string):
		assert isinstance(string, str)
		self.string = string

		self.result = Token(self)

		self.set_intokens([])
		self.set_outtokens([self.result])

		return self.result

	def build(self):
		f = file(self.result.filename(), "w")
		f.write(self.string)
		f.close()
		self.result.finished()

	def identify(self):
		return "FileData(%s)" % self.string.encode("string-escape")

	def change_time(self):
		return datetime.min

class NoDepend(Builder):
	"""NoDepend(token) -> Token
The NoDepend builder returns its argument, except that changes in the input
token will not cause the output calculation to be redone."""
	def start(self, token):
		self.input = token
		self.output = Token(self)

		self.set_intokens([self.input])
		self.set_outtokens([self.output])

		return self.output

	def build(self):
		DoMove(self.input.complete(), self.output.filename())
		self.output.finished()

	def identify(self):
		return "NoDepend(%s)" % self.input.identify()

	def change_time(self):
		# This is the essential part that causes the output calculation not to
		# be redone.
		return datetime.min
