from django.db import connection
from django.http import JsonResponse


def health(request):
    """Liveness and database check for Docker and load balancers."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
