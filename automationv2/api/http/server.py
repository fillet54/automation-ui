import time
import json 
from pathlib import Path
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server, WSGIServer
try:
    from socketserver import ThreadingMixIn
except:
    from SocketServer import ThreadingMixIn

from .qroutes import GET, resource_response, wsgi_adapter, site_handler, not_found_response, file_response, GzipMiddleware, wrap_json_response, route_context
from .navigation import rvt_tree_handler, get_file
from . import tests

MODULE_DIR = Path(__file__).resolve().parent
static_resources = resource_response(MODULE_DIR / "public", default_file='index.html')

def home_handler(request):
    print("HI FROM HOME")
    return {'status': 200,
            'body': b"HELLO WORLD"}

def stream_handler(request):
    def the_stream():
        for i in xrange(10):
            yield 'event: myevent\ndata: {}\n\n\n'.format(i, json.dumps(dict(name="Phillip")))
            time.sleep(10)
    return dict(
        status = 200,
        headers = [('Content-Type', 'text/event-stream')],
        body = the_stream());
    
routes = [
    GET('/api/home', home_handler),
    GET('/api/nav/tree/rvt', rvt_tree_handler),
    GET('/api/nav/file', get_file),
    route_context('/api', tests.routes),
    GET('/stream', stream_handler),
    GET('/*', static_resources)
]
app = site_handler(routes=routes, default_handler=not_found_response)
app = wrap_json_response(app)
app = wsgi_adapter(app)
#app = GzipMiddleware(app)

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True
# This is just a $REQ123 example
if __name__ == '__main__':
    
    PORT = 8056

    httpd = make_server('', PORT, app, ThreadingWSGIServer)

    print("Serving on port {}...".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Exiting")
        httpd.server_close()
