from django.urls import path
from ip import views

app_name = 'ip'

urlpatterns = [
    path('ip/mine/', views.mine, name='ip-mine'),
    path('ip/yours/', views.yours, name='ip-yours'),

]