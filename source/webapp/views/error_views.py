from django.shortcuts import render


def custom_handler404(request, exception=None):
    context = {'error_message': "Такой страницы нет или больше не существует", 'error_title': "page not found"}
    return render(request, 'display_errors.html', context)
