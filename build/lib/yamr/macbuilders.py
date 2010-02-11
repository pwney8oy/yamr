from yamr.builders import *

def MacBundle(oscode=None, infoplist=None, **dirs):
	"""MacBundle(oscode=None, infoplist=None, **dirs) -> Token
Convenience function to create a Mac OS X bundle for an application or plugin. oscode is the OS code
of the bundle; for an application it should be "APPL". infoplist should be a builder for the
info.plist file to be installed at the top level of the bundle. Any other keyword arguments are
interpreted as subdirectories to be installed in the bundle."""
	contents = {}
	
	if oscode: contents["PkgInfo"] = DataFile(oscode+"????")
	if infoplist: contents["Info.plist"] = infoplist
	
	for dirname,dircontents in dirs.iteritems():
		if isinstance(dircontents,Token):
			dir = dircontents
		else:
			dir = MkDir(dircontents)
		contents[dirname] = dir
	
	Contents = MkDir(contents)
	return MkDir({"Contents":Contents})

def MacBundleLibrary(inputs, flags="", keyedinputs=None, bundle_loader=None):
	"""MacBundleLibrary(inputs, flags="", keyedinputs=None, bundle_loader=None) -> Token
Builds a Mac shared library in the 'bundle' style using GCC. Arguments are exactly the same as in
the SharedLibrary builder except that there is an extra one: "bundle_loader". If bundle_loader is
specified, then it will be passed along with the '-bundle_loader' flag to GCC."""
	flags = flags + " -bundle"
	if not keyedinputs:
		keyedinputs = {}
	if bundle_loader:
		keyedinputs["-bundle_loader"] = bundle_loader
	return CCompiler('gcc -o "%%(output)s" -bundle %%(input)s %s' % flags, inputs, keyedinputs)

class InstallNameTool(Builder):
	"""InstallNameTool(source, changes={}, id=None) -> Token
Provides an interface to "install_name_tool -change" and "install_name_tool -id". "source" should be
an executable or shared library to be modified. "changes" provides a set of key-value pairs to be
passed with "-change", and "id" (if not None) provides a new name to be passed with "-id"."""
	def start(self, source, changes={}, id=None):
		self.source = source
		self.changes = changes
		self.id = id
		self.result = Token(self)
		
		self.set_intokens([self.source])
		self.set_outtokens([self.result])
		
		return self.result
	
	def build(self):
		inpath = self.source.complete()
		outpath = self.result.filename()
		DoCopy(inpath, outpath) # install_name_tool operates in place
		
		command = "install_name_tool"
		for old,new in self.changes.iteritems():
			command += " -change %s %s" % (old,new)
		if self.id is not None:
			command += " -id %s"%self.id
		command += " " + outpath
		DoCommand(command)
		
		self.result.finished()
	
	def identify(self):
		return "installnametool(%s,%s,%s)" % (self.source.identify(), self.changes, self.id)