from django.shortcuts import render

# Create your views here.


def vendor_profile(request):
    return render(request, 'vendors/vendor_profile.html')
