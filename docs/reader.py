#cell
import nbloader
nbloader.install_loader()

from nbdev import patch
from functools import reduce

import re

utils = __import__('Appendix - B - Utilities')
#cell

# reader states to run based on character
macros = {}
dispatch_macros = {}

READ_EOF = 'READ_EOF'
READ_FINISHED = 'READ_FINISHED'

def read(stream_or_str, sentinel=None):
    
    if isinstance(stream_or_str, str):
        stream = utils.PushBackCharStream(stream_or_str)
    else:
        stream = stream_or_str
    
    for ch in stream:
        if is_whitespace(ch): continue
        if ch is None: return READ_EOF
        if ch == sentinel: return READ_FINISHED
        
        # Possibly need 1 lookahead
        lookahead = next(stream)
        stream.push_back(lookahead)

        if is_number_literal(ch, lookahead): 
            return read_number(stream, ch)
        elif ch in macros: 
            form = macros[ch](stream, ch)
            
            # if the actual stream is the form then the form was a comment and we should
            # continue on
            if form != stream:
                return form
        else: 
            return read_symbol(stream, ch)
#cell

def is_whitespace(ch):  return ch in ' \t\n,'
def is_ending(ch):      return ch in '";@^`()[]{}\\'
#cell

class Symbol(str):
    def __new__(cls, val, *args, **kwargs):
        return str.__new__(cls, val)

    def __init__(self, val, namespace=None):
        self.namespace = namespace
        self.meta = {}
        
    def __eq__(self, val):
        if isinstance(val, type(self)):
            return super().__eq__(val) and self.namespace == val.namespace
        elif isinstance(val, str):
            if self.namespace is not None:
                return f"{self.namespace}/{self}" == val
            else:
                return super().__eq__(val)
        return False
    
    @property
    def name(self):
        return self
    
    def __repr__(self):
        if self.namespace is None:
            return self
        else:
            return f"{self.namespace}/{self}"
        
    def __hash__(self):
        return hash(str(self))
#cell

def is_special(ch):     return ch in '-+.'
def is_non_numeric(ch): return ch.isalpha() or ch in '.*+!-_?$%&=<>@:#'
def is_start(ch):       return (is_non_numeric(ch) and not ch in ':#')

def is_numeric(ch, base=10):
    try:
        int(ch, base)
        return True
    except:
        return False    

def is_number_literal(ch, lookahead):
    if is_numeric(ch):
        return True
    elif ch == '-' or ch == '+':
        return is_numeric(lookahead)  
    
def read_symbol(stream, initch):
    starting_info = stream.starting_line_col_info()    
    token = read_token(stream, initch)
    
    # Special Symbols
    if token == 'nil': return None
    elif token == 'true': return True
    elif token == 'false': return False
    elif token == '/': return Symbol('/')
    
    try:
        ns, name = parse_symbol(token)
        symbol = Symbol(name, ns)
        
        # attach line/col info
        ending_info = stream.ending_line_col_info()
        symbol.meta['start_row'] = starting_info[0]
        symbol.meta['start_col'] = starting_info[1]
        symbol.meta['ending_row'] = ending_info[0]
        symbol.meta['ending_col'] = ending_info[1]
        
        return symbol
    except:
        raise
        
invalid_token = re.compile(r"(^::|.*:$)")
invalid_namespace = re.compile(r".*:$")
def parse_symbol(token):
    "Parses a string into a tuple of the namespace and symbol"
    if not token or invalid_token.match(token):
        raise Exception("Invalid symbol: '{}'".format(token))
    
    # If no namespace just return None as ns and token as symbol
    if token == '/' or '/' not in token:
        return None, token
    
    ns, sym = token.split('/', 1)
    
    if (sym and 
        not is_numeric(sym[0]) and
        not invalid_namespace.match(ns) and
        (sym == '/' or 
         '/' not in sym)):
        return ns, sym
    raise Exception("Invalid symbol: '{}'".format(token))
    

def read_token(stream, initch):
    token = ''
    
    ch = initch
    while True:
        if ch is None or is_whitespace(ch):
            break
        elif is_ending(ch):
            stream.push_back(ch)
            break
        else:
            token += ch
            ch = next(stream)

    return token
#cell

def read_string(stream, initch):
    s = ''
    for ch in stream:
        if ch == '"':
            break
        elif ch == '\\':
            s += escape_char(stream)
        elif ch is None:
            raise Exception("EOF in middle of string")
        else:
            s += ch
    return s

macros['"'] = read_string

escape_chars = {'t':'\t', 'r':'\r', 'n':'\n', '\\':'\\', '\"':'\"', 'b':'\b', 'f':'\f'}
def escape_char(stream):
    ch = next(stream)
    
    # Normal character
    if ch in escape_chars:
        ch = escape_chars[ch]
    elif ch == 'u':                                    # Hex unicode escape
        ch = read_unicode_char(stream, base=16, length=4)
    elif is_numeric(ch):                      # Octal Unicode escape
        stream.push_back(ch)
        ch = read_unicode_char(stream, base=8, length=3)
    else:
        raise Exception("Invalid escape '\\{}'".format(ch))
    return ch

def read_unicode_char(stream, base, length):
    unicode_bytes = b'\\'
    
    if base == 16:
        unicode_bytes += b'u'

    for _ in range(length):
        ch = next(stream)
        if not is_numeric(ch, base=base):
            raise Exception("Invalid unicode escape '{}'".format(ch))
        unicode_bytes += bytes(ch, 'utf-8')

    try:
        return unicode_bytes.decode('unicode-escape')
    except:
        raise Exception("Invalid unicode escape '{}'".format(unicode_bytes))
#cell

def read_char(stream, initch):
    ch = next(stream)   
    if ch is None:
        raise Exception("EOF in character")
        
    if is_whitespace(ch):
        raise Exception("Backslash cannot be followed by whitespace")
    
    if is_ending(ch):
        token = ch
    else:
        token = read_token(stream, ch)
    
    if len(token) == 1:        ch = token
    elif token == "newline":   ch = '\n'
    elif token == 'space':     ch = ' '
    elif token == 'tab':       ch = '\t'
    elif token == 'backspace': ch = '\b'
    elif token == 'formfeed':  ch = '\f'
    elif token == 'return':    ch = '\r'
    elif token.startswith('u'):
        stream.push_back(token[1:])
        ch = read_unicode_char(stream, base=16, length=4)
    elif token.startswith('o'):
        stream.push_back(token[1:])
        ch = read_unicode_char(stream, base=8, length=len(token)-1)
    else:
        raise Exception("Invalid character escape '{}'".format(token))
    
    return ch

macros['\\'] = read_char
#cell

class Keyword(Symbol):
    pass

    def __repr__(self):
        return ':' + str(self)

def read_keyword(stream, initch):
    starting_info = stream.starting_line_col_info()
    
    ch = next(stream)
    if is_whitespace(ch):
        raise Exception('Single colon not allowed')
    
    token = read_token(stream, ch)
    ns, kw = parse_symbol(token)
    
    if ns is not None and ns.startswith(':'):
        raise Exception('Namespace alias not supported')
    
    keyword = Keyword(kw, ns)
    
    # attach line/col info
    ending_info = stream.ending_line_col_info()
    keyword.meta['start_row'] = starting_info[0]
    keyword.meta['start_col'] = starting_info[1]
    keyword.meta['ending_row'] = ending_info[0]
    keyword.meta['ending_col'] = ending_info[1]
    
    return keyword
        
macros[':'] = read_keyword
#cell

int_pattern = re.compile(r"^([-+]?)(?:(0)|([1-9][0-9]*)|0[xX]([0-9A-Fa-f]+)|0([0-7]+)|([1-9][0-9]?)[rR]([0-9A-Za-z]+)|0[0-9]+)(N)?$")

def read_number(stream, initch):
    s = initch
    for ch in stream:
        if ch is None or is_whitespace(ch) or is_ending(ch):
            stream.push_back(ch)
            return match_number(s)
        else:
            s += ch

def match_number(s):
    if int_pattern.match(s):
        return match_int(s)
    elif float_pattern.match(s):
        return match_float(s)
    elif ratio_pattern.match(s):
        return match_ratio(s)
    
def match_int(s):
    m = int_pattern.match(s).groups()
    if m[1] is not None:
        return 0
    
    negate = m[0] == '-'
    
    if m[2] is not None:
        base = 10
        n = m[2]
    elif m[3] is not None:
        base = 16
        n = m[3]
    elif m[4] is not None:
        base = 8
        n = m[4]
    elif m[6] is not None:
        base = int(m[5])
        n = m[6]
    else:
        base = None
        n = None
        
    number = int(n, base)
    number = -1 * number if negate else number
    return number
#cell

float_pattern = re.compile(r"^([-+]?[0-9]+(\.[0-9]*)?([eE][-+]?[0-9]+)?)(M)?$")
ratio_pattern = re.compile(r"^([-+]?[0-9]+)/([0-9]+)$")

def match_float(s):
    m = float_pattern.match(s).groups()
    if m[3] is not None:
        return float(m[0])   # TODO: Should we support exact precision? This would be decimal.Decimal
    else:
        return float(s)
    
def match_ratio(s):
    m = ratio_pattern.match(s).groups()
    numerator = m[0][1:] if m[0].startswith('+') else m[0]
    denominator = m[1]    
    
    # no ratio in python
    return int(numerator) / int(denominator)
#cell
class List(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = {}

def read_list(stream, initch):
    starting_info = stream.starting_line_col_info()
    
    forms = read_delimited(stream, initch, sentinel=')')
    thelist = List(forms)
    
    # attach line/col info
    ending_info = stream.ending_line_col_info()
    thelist.meta['start_row'] = starting_info[0]
    thelist.meta['start_col'] = starting_info[1]
    thelist.meta['ending_row'] = ending_info[0]
    thelist.meta['ending_col'] = ending_info[1]
    
    return thelist

def read_delimited(stream, initch, sentinel):
    starting_info = stream.starting_line_col_info()
    
    forms = []
    while True:
        form = read(stream, sentinel)
        if form == READ_EOF:
            raise Exception("EOF in middle of list")
        elif form == READ_FINISHED:
            return forms
        elif form == stream:
            pass
        else:
            forms.append(form)

macros['('] = read_list
        
#cell
class Vector(List):
    pass

def read_vector(stream, initch):
    starting_info = stream.starting_line_col_info()
    forms = read_delimited(stream, initch, sentinel=']')
    thevector = Vector(forms)
    
    # attach line/col info
    ending_info = stream.ending_line_col_info()
    thevector.meta['start_row'] = starting_info[0]
    thevector.meta['start_col'] = starting_info[1]
    thevector.meta['ending_row'] = ending_info[0]
    thevector.meta['ending_col'] = ending_info[1]
    
    return thevector

macros['['] = read_vector
#cell
class Map(dict):
    def __init__(self, vals, linerange=None):
        dict.__init__(self, vals)
        self.meta = {}
    
def read_map(stream, initch):
    starting_info = stream.starting_line_col_info()
    forms = read_delimited(stream, initch, sentinel='}')
    
    assert len(forms) % 2 == 0, "Map must have value for every key"
    
    pairs = [forms[i:i+2] for i in range(0, len(forms), 2)]   
    themap = Map(pairs)
    
    # attach line/col info
    ending_info = stream.ending_line_col_info()
    themap.meta['start_row'] = starting_info[0]
    themap.meta['start_col'] = starting_info[1]
    themap.meta['ending_row'] = ending_info[0]
    themap.meta['ending_col'] = ending_info[1]
    
    return themap

macros['{'] = read_map
#cell

def read_dispatch(stream, initch):
    ch = next(stream)
    if ch in dispatch_macros:
        return dispatch_macros[ch](stream, ch)
    raise Exception("Invalid Dispatch")
    
macros['#'] = read_dispatch 

class Set(set):
    def __init__(self, *vals):
        set.__init__(self, vals)
        self.meta = {}
        
def read_set(stream, initch):
    starting_info = stream.starting_line_col_info()
    
    forms = read_delimited(stream, initch, sentinel='}')
    theset = Set(*forms)
    
    # attach line/col info
    ending_info = stream.ending_line_col_info()
    theset.meta['start_row'] = starting_info[0]
    theset.meta['start_col'] = starting_info[1] - 1
    theset.meta['ending_row'] = ending_info[0]
    theset.meta['ending_col'] = ending_info[1]
    
    return theset

dispatch_macros['{'] = read_set
#cell

def read_comment(stream, initch):
    for ch in stream:
        if ch == '\n':
            break
        # ignore everything else
    # returning the stream will allow higher level
    # macros ignore the form.
    return stream
macros[';'] = read_comment
