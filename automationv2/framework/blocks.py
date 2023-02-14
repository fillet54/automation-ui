class BuildingBlock:
    ''' 
    The 'BuildingBlock' of the automation framework. Registers a function to
    be run during test execution.
    '''
    def name(self):
        '''Returns the name of the building block. The name is used
        as a first order lookup for the block'''
        return type(self).__name__
    
    def check_syntax(self, *args):
        '''Returns True if this BuildingBlock can support the arguments and False otherwise'''
        return True
    
    def execute(self, *args):
        '''Executes the block. Returns a BlockResult'''
        return BlockResult(False)

class BlockResult:
    '''
    The result of executing a BuildingBlock
    '''
    def __init__(self, passed, stdout="", stderr=""):
        self.passed = passed
        self.stdout = stdout
        self.stderr = stderr
        
    def __bool__(self):
        return self.passed
    
    def __str__(self):
        return "<BlockResult: %s, stdout=%s, stderr=%s>" % ('PASS' if self.passed else 'FAIL', self.stdout, self.stderr) 