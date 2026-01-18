# Django REST Framework (DRF)
# https://www.django-rest-framework.org/
REST_FRAMEWORK = {
    # Renderer/parsers translate between camelCase and snake_case at application
    # entry, allowing clients to send/receive data as camelCase while we can still
    # use snake_case within this application
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
    ),
    "JSON_UNDERSCOREIZE": {"no_underscore_before_number": True},
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}
