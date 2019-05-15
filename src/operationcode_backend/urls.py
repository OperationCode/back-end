from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    path("", include("backend.urls")),
    path("api/v1/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("docs/", get_swagger_view(title="OperationCode API"), name="api_docs"),
]

##############################################
#   Static and media files in debug mode     #
##############################################
if settings.DEBUG or settings.TESTING:
    import debug_toolbar

    urlpatterns += [
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        path("__debug__/", include(debug_toolbar.urls)),
    ]
