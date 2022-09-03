import re
import json
import os
import mimetypes

try:
    import urlparse
    import httplib
except:
    import urllib.parse as urlparse
    import http.client as httplib

def re_groups(matcher):
    for i in range(len(matcher.groups())):
        yield matcher.group(i+1)

def put_list(d, k, v):
    "Puts a key with a value into dictionary. If key already exists in dict, create list of values"
    cur = d.get(k, None)
    if cur:
        if isinstance(cur, list):
            cur.append(v)
            v = cur
        else:
            v = [cur, v] 
    d[k] = v

def put_keys_with_groups(groups, keys):
    d = dict()
    for (k, v) in zip(keys, groups):
        put_list(d, k, v)
    return d

def lex_1(src, clauses):
    """Scan one symbol from src and return a tuple of the symbol and remaining src"""
    for (regex, action) in clauses:
        matcher = re.match(regex, src)
        if matcher:
            if callable(action):
                action = action(matcher)
            return (action, src[matcher.end():])
    return None

def lex(src, clauses):
    """Return a list of symbols from string based on clauses. Clauses is a list of
       regex pattern and either replacement text or function that takes the match and 
       returns replacement text"""
    results = []
    while src != "":
        (result, src) = lex_1(src, clauses)
        results.append(result)
    return results

#re_word    = r":([\p{L}_][\p{L}_0-9-]*)"
#re_literal = r"(:[^\p{L}_*]|[^:*])+"
re_word    = r":(\w\w*)"
re_literal = r"(:[^\w*]|[^:*])+"

def word_group(matcher):
    return matcher.group(1)

def build_route_regex(path, regexs):
    def re_word_action(matcher):
        return "(%s)" % regexs.get(word_group(matcher), "[^/,;?]+")
    def re_literal_action(matcher):
        return re.escape(matcher.group())
    clauses = [(r"\*",     "(.*?)"),
               (re_word,    re_word_action),
               (re_literal, re_literal_action)]
    parts = lex(path, clauses)
    parts.append("\\Z")
    return "".join(parts)

def find_path_keys(path):
    clauses = [(r"\*", "*"),
               (re_word, word_group),
               (re_literal, None)]
    return filter(lambda x: x != None, lex(path, clauses))

class CompiledRoute(object):
    def __init__(self, source, regex, keys):
        self.source = source 
        self.regex = re.compile(regex)
        self.keys = keys

    def route_matches(self, request):
        path_info = request.get("uri")
        matcher = self.regex.match(path_info)
        if matcher:
            return put_keys_with_groups(re_groups(matcher), self.keys)
        
        # Add trailing slash
        path_info = path_info + "/"
        matcher = self.regex.match(path_info)
        if matcher:
            return put_keys_with_groups(re_groups(matcher), self.keys)

        return None

def route_compile(path, regexs=dict()):
    path_keys = find_path_keys(path)
    return CompiledRoute(path, 
                         build_route_regex(path, regexs), 
                         path_keys)

################################################################################
# ROUTER API
################################################################################

def method_matches (request, method):
    '''Determines if request method matches specified option
    TODO: Form post
    
    >>> method_matches({'request-method': 'GET'}, 'GET')
    True
    >>> method_matches({'request-method': 'HEAD'}, 'GET')
    True
    >>> method_matches({'request-method': 'GET'}, 'POST')
    False
    '''
    if method == None:
        return True

    request_method = request.get("request-method")

    if request_method == "HEAD":
        return method == "HEAD" or method == "GET"
    return request_method == method

def make_route(method, path, handler):
    return dict(method=method,
                path=path,
                handler=handler)

def GET(path, handler):
    return make_route("GET", path, handler)

def POST(path, handler):
    return make_route("POST", path, handler)

def route_context(context, *routes):
    return dict(context=context,
                routes=routes)

def not_found_response(request):
    return {
        'status': 404,
        'headers': [('Content-type','text/plain')],
        'body': "Not Found"
    }

def site_handler(routes=[], default_handler=None):
    '''Takes list set of routes and returns a handler that will
    match request uri. When match is found handler function is called
    else default handler is called.

    '''
    routes = routes if isinstance(routes, list) else [routes]

    def build_routes(l, route, context=""):
        if isinstance(route, (list, tuple)):
            for r in route:
                build_routes(l, r, context)
        elif "context" in route:
            for r in route["routes"]:
                build_routes(l, r, context+route['context'])
        else:
            route['full_path'] = "%s%s" % (context, route['path'])
            route['context'] = context
            route['compiled'] = route_compile(route['full_path'])
            l.append(route)

    complete_routes = []
    for route in routes:
        build_routes(complete_routes, route)

    def router_handler(request):
        for route in complete_routes:
            if method_matches(request, route.get('method', None)):
                route_params = route['compiled'].route_matches(request)
                if route_params is not None:
                   request['params'] = route_params
                   request['context'] = route['context']
                   request['path-info'] = request['path-info'][len(route['context']):] 
                   response = route['handler'](request)
                   if response is not None:
                       return response
        if default_handler is not None:
            return default_handler(request)
        else:
            return None
    return router_handler

class UnknownHTTPStatus(Exception):
    pass

def wsgi_environ_to_ring_request(environ):
    '''Convert wsgi environment to a ring request

    '''
    ring_request = {} 

    if 'wsgi.input' in ring_request:
        ring_request['body'] = ring_request['wsgi.input'].read()
        del ring_request['wsgi.input']

    mappings = [
        ('SERVER_PORT', 'server-port'),
        ('SERVER_NAME', 'server-name'),
        ('REMOTE_ADDR', 'remote-addr'),
        ('PATH_INFO', 'uri'),
        ('PATH_INFO', 'path-info'),
        ('QUERY_STRING', 'query-string'),
        ('wsgi.url_scheme', 'scheme'),
        ('REQUEST_METHOD', 'request-method'),
        ('SERVER_PROTOCOL', 'protocol'),
    ]

    for wsgi, ring in mappings:
        if wsgi in environ:
            ring_request[ring] = environ[wsgi]

    # headers
    ring_request['headers'] = {}
    header_keys = [k for k in environ if k.startswith('HTTP_')]
    for k in header_keys:
        header_name = '-'.join([w.lower().capitalize() for w in k[5:].split('_')])
        ring_request['headers'][header_name] = environ[k]

    # special header cases 
    for _from, to in (('CONTENT_TYPE', 'Content-Type'), ('CONTENT_LENGTH', 'Content-Length')):
        if _from in environ:
            ring_request['headers'][to] = environ[_from]

    return ring_request

def wsgi_adapter(handler):
    '''Router framework expects to receive a response map. This middleware
    will take that response map and call the appropriate wsgi calls
    
    '''
    def wsgi_handler(environ, start_response):
        request = wsgi_environ_to_ring_request(environ)
        response = handler(request)
        status = 200
        headers = []
        if isinstance(response, dict):
            status = response.get('status', status)
            body = response.get('body', [])
            headers = response.get('headers', [])
        else:
            body = response

        if isinstance(status, int) and status in httplib.responses:
            status = '{0} {1}'.format(status, httplib.responses[status])
        elif not isinstance(status, str):
            raise UnknownHTTPStatus('Unknown response code {0}'.format(status))

        start_response(status, headers)
        if isinstance(body, (str, bytes)):
            return [body]
        else:
            return body
    return wsgi_handler

################################################################################
# Middleware  
################################################################################

def wrap_query_params(handler):
    '''Parse the query string into both a list, which maintains order
    including duplicate keys, and a dictionary that will not maintain order
    and only contain the last query param on duplicates 

    '''
    def query_params(request):
         query_string_list = urlparse.parse_qsl(request.get('query-string', ''))
         request['query-params-list'] = query_string_list
         request['query-params'] = dict(query_string_list)
         return handler(request)
    return query_params

def wrap_json_response(handler):
    '''Converts body to json if headers indicate json

    '''
    pretty_pattern = re.compile(r'(^pretty$)|([\&]*pretty\&)')
    def pretty(request):
        query_string = request.get('query-string', '')
        query_params = request.get('query-params', {})
        return pretty_pattern.search(query_string) is not None \
               or query_params.get('pretty', '').lower() == 'true'

    def json_response_handler(request):
        response = handler(request)
        if isinstance(response, dict) and 'body' in response:
            if not isinstance(response['body'], (list, dict, tuple)):
                # Don't know how to convert. Either already converted
                # i.e String/File or something else down the pipeline
                # knows what to do
                return response
            headers = dict(response.get('headers', []))
            content_type = headers.get('Content-Type', '')
            if content_type.endswith('/json') or content_type.endswith('+json'):
                if pretty(request):
                   response['body'] = json.dumps(response['body'], 
                                                  indent=4 )
                else:
                    response['body'] = json.dumps(response['body']) 
                response['body'] = response['body'].encode('utf-8')
        return response
    return json_response_handler

def wrap_config(handler, config):
    '''Middleware that inserts config into request object

    '''
    def config_handler(request):
        request['config'] = config
        return handler(request)
    return config_handler

# Gzip
from gzip import GzipFile
from wsgiref.headers import Headers
import re

try:
    from io import StringIO, BytesIO
except:
    from cStringIO import StringIO


# Precompile the regex to check for gzip headers
re_accepts_gzip = re.compile(r'\bgzip\b')

# Precompile the regex to split a comma delimitered string of Vary headers
cc_delim_re = re.compile(r'\s*,\s*')


def gzip_buffer(string, compression_level=6):
    """gzips a string."""
    zbuf = BytesIO()
    f = GzipFile(filename=None, mode='wb',
            compresslevel=compression_level, fileobj=zbuf)
    f.write(string)
    f.close()
    return zbuf.getvalue()


def client_accepts_gzip(environ):
    """Checks whether the client accepts gzipped output."""
    accept_header = environ.get('HTTP_ACCEPT_ENCODING', '')
    return re_accepts_gzip.search(accept_header)


def patch_vary_headers(headers, new_values):
    """Patches any existing Vary headers to add new_values to it.  Returns
    nothing, but modifies the headers array in-place.
    """
    if 'vary' in headers:
        vary_headers = cc_delim_re.split(headers['vary'])
    else:
        vary_headers = []

    existing_values = set([header.lower() for header in vary_headers])
    additional_values = [new_value for new_value in new_values
                         if new_value.lower() not in existing_values]
    headers['Vary'] = ', '.join(vary_headers + additional_values)


class GzipMiddleware(object):
    """The actual WSGI middleware to wrap around your app and gzip all output.
    This automatically adds the required HTTP headers.
    """
    def __init__(self, app, compresslevel=6):
        self.app = app
        self.compresslevel = compresslevel

    def __call__(self, environ, start_response):
        if not client_accepts_gzip(environ):
            return self.app(environ, start_response)

        def collect_response(response):
            """Intercepts the response from the WSGI app, and stores the
            output in the given response dict for later inspection.
            """
            def _intercept_response(status, headers, *args, **kwargs):
                response['status'] = status
                response['headers'] = headers

            return _intercept_response

        def to_bytes(s):
            if isinstance(s, str):
                return s.encode('utf-8')
            else:
                return s

        # Now get the raw response from the WSGI app
        app_response = {}

        try:
            iterable = self.app(environ, collect_response(app_response))

            # encode strings to utf-8
            raw_response = b''.join(to_bytes(s) for s in iterable)

            def pass_through(app_response, raw_response):
                start_response(app_response['status'], app_response['headers'])
                return [raw_response]

            headers = Headers(app_response['headers'])
            if 'content-encoding' in headers:
                # Since there already is a content encoding, apparently, we just
                # return the respons without compression
                return pass_through(app_response, raw_response)

            # Perform the gzip
            buflen = len(raw_response)
            if buflen <= 200:
                return pass_through(app_response, raw_response)
            gzipped_response = gzip_buffer(raw_response)

            # Last check: only send the response if it's actually shorter
            if len(gzipped_response) >= buflen:
                return pass_through(app_response, raw_response)
            del raw_response  # garbage collect early

            # Set headers accordingly
            headers['Content-Encoding'] = 'gzip'
            headers['Content-Length'] = str(len(gzipped_response))
            if 'ETag' in headers:
                headers['ETag'] = re.sub('"$', ';gzip"', headers['ETag'])
            patch_vary_headers(headers, ('Accept-Encoding',))

            # Send the headers and the contents
            start_response(app_response['status'], app_response['headers'])
            return [gzipped_response]
        finally:
            if hasattr(iterable, 'close'):
                iterable.close()

################################################################################
# Response
################################################################################
def redirect_response(request, path, code=301):
    location = '{0}://{1}{2}'.format(request['scheme'], request['headers']['Host'], path)
    REDIRECT_CODES = [301, 302, 303, 307, 308]
    assert code in REDIRECT_CODES, 'Redirect code must be in {0}'.format(REDIRECT_CODES)
    return {
        'status': code,
        'headers': [('Location', location)]
    }

def redirect(path, code=301):
    def redirect_handler(request):
        return redirect_response(request, path, code)
    return redirect_handler

class FileWrapper(object):
    def __init__(self, file, buffer_size=8192):
        self.file = file
        self.buffer_size = buffer_size

    def close(self):
        if hasattr(self.file, 'close'):
            self.file.close()

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        data = self.file.read(self.buffer_size)
        if data:
            return data
        raise StopIteration()

default_mime = 'application/octet-stream'
extended_mimes = {
    'manifest': 'text/cache-manifest',
    'html': 'text/html',
    'png': 'image/png',
    'jpg': 'image/jpg',
    'svg': 'image/svg+xml',
    'css': 'text/css',
    'jsx': 'text/jsx',
    'js':  'application/x-javascript'
}

def file_response(path, defaultType=default_mime):
    def response(request):
        extension = path.split('.')[-1]
        guessed_type = mimetypes.guess_type(path)
        mime_type = extended_mimes.get(extension, guessed_type[0] or defaultType) 
        file = open(path, 'rb')
        file_size = os.path.getsize(path)
        headers = [('Content-Type', mime_type),
                   ('Content-Length', str(file_size)),
                   ('Cache-Control', 'public')]
        return {
            'status': 200,
            'headers': headers,
            'body': FileWrapper(file)
        }
    return response

def resource_response(root, default_file='', defaultType=default_mime):
    def response(request):
        path = request['path-info']
        context = request.get('context', '')
        full_path = root + path

        if not os.path.isfile(full_path):
            full_path = "/".join([root, default_file])
            if default_file == '' or not os.path.exists(full_path):
                return None 

        print("FULLPATH", full_path)
        extension = full_path.split('.')[-1]
        guessed_type = mimetypes.guess_type(full_path)
        mime_type = extended_mimes.get(extension, guessed_type[0] or defaultType) 
        file = open(full_path, 'rb')
        file_size = os.path.getsize(full_path)
        
        headers = [('Content-Type', mime_type),
                   ('Content-Length', str(file_size)),
                   ('Cache-Control', 'public')]

        return {
            'status': 200,
            'headers': headers,
            'body': FileWrapper(file)
        }

    return response


if __name__ == '__main__':
    import doctest
    doctest.testmod()
