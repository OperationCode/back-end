from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="OperationCode API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://operationcode.org/terms/",
        contact=openapi.Contact(email="staff@operationcode.org"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", include("core.urls")),
    path("", include("frontend.urls")),
    path("api/v1/", include("api.urls")),
    path("admin/", admin.site.urls),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

##############################################
#    Static and media files in debug mode    #
##############################################
if settings.DEBUG or settings.TESTING:
    import debug_toolbar

    urlpatterns += [
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        path("__debug__/", include(debug_toolbar.urls)),
    ]
