from functools import wraps

from django.http import HttpResponseBadRequest
from django.utils.log import log_response


def require_headers(headers_dict):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            for header, value in headers_dict.items():
                if request.headers.get(header) != value:
                    response = HttpResponseBadRequest()
                    log_response(
                        "Header Value Not Allowed (%s, value '%s') for path %s",
                        header,
                        request.headers.get(header),
                        request.path,
                        response=response,
                        request=request,
                    )
                    return response
            return func(request, *args, **kwargs)

        return inner

    return decorator
