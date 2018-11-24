from django.urls import path

from . import views

urlpatterns = [
    path('daily/', views.daily, name='daily'),
    path('daily/data/', views.questions_daily_data, name='questions_daily_data'),
    path('monthly/', views.monthly, name='monthly'),
    path('monthly/data/', views.questions_monthly_data, name='questions_monthly_data'),
]