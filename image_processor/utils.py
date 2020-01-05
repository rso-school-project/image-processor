""" Utils module """
import etcd3

from functools import wraps
from func_timeout import FunctionTimedOut

from starlette.responses import JSONResponse, Response
from starlette.requests import Request


from image_processor import ETCD_HOST_PORT, ETCD_HOST_URL


def fallback(fallback_function):
    def outer_wrapper(f):

        # will preserve information about the original function.
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            # TODO: Remove generic Exception type in the future :).
            except (FunctionTimedOut, Exception) as ex:
                return fallback_function()

        return inner_wrapper

    return outer_wrapper


# health checks implementation:
#   - https://inadarei.github.io/rfc-healthcheck/#rfc.section.3
#   - https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/


def health_check_failure():
    return {'status': 'fail'}


@fallback(fallback_function=health_check_failure)
def check_etcd_connection():
    etcd = etcd3.client(host=ETCD_HOST_URL, port=ETCD_HOST_PORT)
    etcd.status()
    return {'status': 'pass'}



def check_liveness(request: Request) -> Response:
    data = {'status': 'pass', 'checks': {'etcd:status': [check_etcd_connection()],
                                         'postgres:status': [check_etcd_connection()]}}
    return JSONResponse(content=data, media_type='application/health+json')


def check_readiness(request: Request) -> Response:
    data = {'status': 'pass', 'checks': {'etcd:status': [check_etcd_connection()],
                                         'postgres:status': [check_etcd_connection()]}}
    return JSONResponse(content=data, media_type='application/health+json')
