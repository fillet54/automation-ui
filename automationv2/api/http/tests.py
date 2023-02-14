
from .qroutes import context, JSON_CONTENT, SUCCESS


test_context = context('/tests')

@test_context.GET('/')
def tests(request):
    return {
        'status': 200,
        'body': b"TESTING"
    }

@test_context.GET('/:id')
def test(request):
    print(request)
    id = request['params']['id']
    return SUCCESS(headers=JSON_CONTENT, body={
        'status': 200,
        'body': f"TEST with id {id}"
    })

routes = test_context.routes