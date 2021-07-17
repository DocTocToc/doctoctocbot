from django.shortcuts import render
from choice.models import School
from djgeojson.views import GeoJSONLayerView

class SchoolGeoJSONLayerView(GeoJSONLayerView):
    geometry_field = 'geometry'
    properties=['popup', 'slug', 'tooltip',]
    model = School

    def get_queryset(self):
        qs = super(SchoolGeoJSONLayerView, self).get_queryset()
        return qs.filter(active=True)
