import hmac
from hashlib import sha256
from logging import getLogger

from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django_q.tasks import async_task

from .decorators import require_headers

log = getLogger(__name__)


@require_http_methods(["GET", "POST"])
@require_headers({"User-Agent": "DropboxWebhooks/1.0"})
@csrf_exempt
def dropbox_hook(request):
    if request.method == "GET":
        response = HttpResponse(request.GET.get("challenge"))
        response["Content-Type"] = "text/plain"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    # Make sure this is a valid request from Dropbox
    try:
        signature = request.headers.get("X-Dropbox-Signature")
        valid_signature = hmac.compare_digest(
            signature,
            hmac.new(
                settings.DROPBOX["app_secret"].encode("ascii"), request.body, sha256
            ).hexdigest(),
        )
    except Exception:
        valid_signature = False
    if not valid_signature:
        return HttpResponseBadRequest()

    async_task("django.core.management.call_command", "dropbox_import")
    return HttpResponse("thanks")
