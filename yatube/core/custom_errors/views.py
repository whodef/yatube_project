from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/custom_errors/404.html', {'path': request.path}, status=404)


def permission_denied(request, exception):
    return render(request, 'core/custom_errors/403.html', {'path': request.path}, status=403)


def csrf_failure(request, reason=''):
    return render(request, 'core/custom_errors/403csrf.html')


def server_error(request):
    return render(request, 'core/custom_errors/500.html', {'path': request.path}, status=500)
