from django.shortcuts import render


def landing(request):
    """Vista de la página de inicio (landing page)"""
    return render(request, 'core/landing.html')
