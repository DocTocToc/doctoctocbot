from django.urls import path
from ip import views

app_name = 'ip'

urlpatterns = [
    path('ip/mine/', views.ip_mine, name='ip-mine'),
    path('ip/yours/', views.ip_yours, name='ip-yours'),

]