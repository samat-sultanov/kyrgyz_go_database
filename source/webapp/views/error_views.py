from django.shortcuts import render


def custom_handler400(request, exception):
    response = render(request, '400.html')
    response.status_code = 400
    return response


def custom_handler403(request, exception):
    response = render(request, '403.html')
    response.status_code = 403
    return response


def custom_handler404(request, exception):
    response = render(request, '404.html')
    response.status_code = 404
    return response


def custom_handler500(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response
