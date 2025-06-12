from django.shortcuts import render

def home(request):
    """
    Renders the home page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'home.html' template.
    """
    return render(request, 'home.html')
