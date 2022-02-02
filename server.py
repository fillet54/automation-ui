from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server, WSGIServer
from SocketServer import ThreadingMixIn

from qroutes import GET, resource_response, wsgi_adapter, site_handler, not_found_response, file_response

static_resources = resource_response('./public', default_file='index.html')

def home_handler(request):
    print("HI FROM HOME")
    return {'status': 200,
            'body': b"HELLO WORLD"}

routes = [
    GET('/api/home', home_handler),

    GET('/*', static_resources)
]
app = site_handler(routes=routes, default_handler=not_found_response)

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True

if __name__ == '__main__':
    
    PORT = 8056

    httpd = make_server('', PORT, wsgi_adapter(app), ThreadingWSGIServer)

    print("Serving on port {}...".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Exiting")
        httpd.server_close()