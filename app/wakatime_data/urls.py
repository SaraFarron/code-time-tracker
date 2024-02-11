from django.http.request import HttpRequest
from django.urls import path
from ninja_extra import NinjaExtraAPI, api_controller, http_get, permissions
from wakatime_data.config import WakatimeAPI
from wakatime_data.models import *

api = NinjaExtraAPI()


@api_controller(
    "/dumps/",
    tags=["Dumps"],
    permissions=permissions.IsAuthenticated
)
class WakaDumps:
    @http_get("/download/")
    def download(self, request: HttpRequest):
        profile = Profile.objects.get(user=request.user)
        wa = WakatimeAPI(profile.wakatime_token)
        result = wa.create_dump()
        if result is None:
            return 200, {"message": "Success"}
        return 400, {"message": result}


@api.get("/test/")
def test(request):
    return {"message": "Hello World"}


urlpatterns = [
    path('', api.urls),
]
