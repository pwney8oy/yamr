from yamr.actions import *
from datetime import datetime
import os, hashlib
os.stat_float_times(False)

__all__ = ["Token", "Builder", "Export"]

def mtime(filename):
    mt = os.stat(filename).st_mtime
    if os.path.isdir(filename):
        submts = [os.stat(os.path.join(filename,n)).st_mtime
                  for n in os.listdir(filename)]
        mt = max(submts+[mt])
    return datetime.fromtimestamp(mt)


class Token(object):
    def __init__(self, builder, extraid = None, filename = None):
        self.builder = builder
        self.extraid = extraid
        
        self.fname = filename
        if not self.fname:
            hash = hashlib.md5(self.identify()).digest().encode("hex")
            self.fname = "yamrbuild/%s" % hash
            self.done = False
        else:
            self.done = True

    def complete(self):
        if not self.done:
            self.builder.perform()

        return self.filename()

    def finished(self):
        assert not self.done, "Token.finished() called twice!"
        self.done = True

    def filename(self):
        return self.fname

    def identify(self):
        if self.extraid:
            return self.builder.identify() + str(self.extraid)
        else:
            return self.builder.identify()


class Builder(object):

    class __metaclass__(type):
        def __call__(cls, *args, **kwargs):
            instance = cls.__new__(cls)
            
            result = instance.start(*args, **kwargs)
            assert instance.intokens!=None
            assert instance.outtokens!=None

            return result

    def __init__(self):
        self.intokens = None
        self.outtokens = None

    def start(self, *args, **kwargs):
        raise NotImplementedError

    def is_rebuild_required(self):
        if not self.outtokens:
            return True

        fn = self.outtokens[0].filename()
        if not os.path.exists(fn):
            return True
        if self.change_time() > mtime(fn):
            return True
        
        return False

    def perform(self):
        if self.is_rebuild_required():
            self.clean()
            self.build()
        else:
            for token in self.outtokens:
                token.finished()

    def clean(self):
        for token in self.outtokens:
            fn = token.filename()
            if os.path.exists(fn):
                DoRemove(fn)

    def set_intokens(self, tokens):
        assert all(isinstance(x,Token) for x in tokens)
        self.intokens = tokens

    def set_outtokens(self, tokens):
        assert all(isinstance(x,Token) for x in tokens)
        self.outtokens = tokens

    def change_time(self):
        ctimes = [x.builder.change_time() for x in self.intokens]
        if ctimes:
            return max(ctimes)
        else:
            return datetime.min


def Export(token, filename):
    srcfilename = token.complete()

    if not os.path.exists(filename) or mtime(srcfilename) > mtime(filename):
        if os.path.exists(filename):
            DoRemove(filename)
        DoCopy(token.complete(), filename)

    print "[YAMR: Finished exporting to \"%s\".]" % filename
