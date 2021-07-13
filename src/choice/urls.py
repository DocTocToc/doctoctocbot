from djgeojson.views import GeoJSONLayerView
from django.views.generic import TemplateView
from choice.models import School
from django.urls import include, path
from rest_framework import routers
from choice.api import views

app_name = 'choice'

router = routers.DefaultRouter()
router.register(r'diploma', views.DiplomaViewSet)
router.register(r'discipline', views.DisciplineViewSet)
router.register(r'participant-type', views.ParticipantTypeViewSet)
router.register(r'participant-room', views.ParticipantRoomViewSet)


urlpatterns = [
    path(
        'data/school/',
        GeoJSONLayerView.as_view(
            model=School,
            geometry_field = 'geometry',
            properties=['popup', 'slug', 'tooltip',]    
        ),
        name='school-geojson'
    ),
    #path(
    #    '',
    #    TemplateView.as_view(template_name='choice/schools.html'),
    #    name='home'
    #),
    path(
        '',
        TemplateView.as_view(template_name='choice/index.html'),
        name='home'
    ),
    path(
        'api/',
        include(router.urls)
    ),
    path('api/create-room/<slug:role>/<slug:school>/<slug:diploma>/',
        views.CreateRoom.as_view()
    ),
    path('api/inactivate-room/<slug:school>/<slug:diploma>/',
        views.InactivateRoom.as_view()
    ),
]