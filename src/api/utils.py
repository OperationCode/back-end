from django.http import JsonResponse


def error_response(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)
