from django.urls import path

from . import views

app_name = 'charts'

urlpatterns = [
    path('daily/', views.daily, name='daily'),
    path('daily/data/', views.questions_daily_data, name='questions_daily_data'),
    path('monthly/', views.monthly, name='monthly'),
    path('monthly/data/', views.questions_monthly_data, name='questions_monthly_data'),
    path('yearly/', views.yearly, name='yearly'),
    path('yearly/data/', views.questions_yearly_data, name='questions_yearly_data'),

]