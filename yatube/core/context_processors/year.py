from django.utils import timezone


def year(request):
    """Переменная с текущим годом, через модуль Django."""
    return {
        'year': timezone.now().year,
    }
