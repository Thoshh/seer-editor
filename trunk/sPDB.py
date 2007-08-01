import bdb
import sys

class sPdb(bdb.Bdb):
    """ Subclass of bdb that sends output to the prompt window """

    def __init__(self, sFrame):
        """ Set up for debugging """
        bdb.Bdb.__init__(self)

        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr

        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None

        self.sFrame = sFrame

    def start(self,debugfile,globals=None,locals=None):
        """ Start debugging """

        # redirect output to prompt window
        #sys.stdout = sys.stderr = self.sFrame.txtPrompt
        cmd = 'execfile("' + debugfile + '")'
        self.run(cmd,globals,locals)

        # get output back to original
        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr

