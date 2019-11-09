from django.urls import include, path
from rest_framework import routers
from optin import views

app_name = 'optin'

#router = routers.DefaultRouter()
#router.register(r'moderators', views.ModeratorViewSet)

urlpatterns = [
#    path('api/', include(router.urls)),
#    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/get/', views.get_optin_view, name='get'),
    path('api/update/', views.update_optin_view, name='update')
]