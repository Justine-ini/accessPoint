from django.shortcuts import render
from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from vendor.models import Vendor


def get_or_set_current_location(request):
    if "lat" in request.session and "lng" in request.session:
        return float(request.session["lng"]), float(request.session["lat"])
    elif "lat" in request.GET and "lng" in request.GET:
        lat = float(request.GET["lat"])
        lng = float(request.GET["lng"])
        request.session["lat"] = lat
        request.session["lng"] = lng
        return lng, lat
    else:
        return None


def home(request):
    location = get_or_set_current_location(request)
    if location:
        lng, lat = location
        pnt = GEOSGeometry(f'POINT({lng} {lat})', srid=4326)

        vendors = (Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=1000)))
                   .annotate(distance=Distance("user_profile__location", pnt))
                   .order_by("distance"))

        # Round off km on each vendor
        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 2)
    else:
        # Fallback: just show the first 8 approved vendors
        vendors = Vendor.objects.filter(
            is_approved=True,
            user__is_active=True)[:8]

    return render(request, "home.html", {"vendors": vendors})
