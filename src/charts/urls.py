from django.urls import path

from charts.views import question, creation_follower, reply_delay

app_name = 'charts'

urlpatterns = [
    path('daily/', question.daily, name='daily'),
    path('daily/data/', question.questions_daily_data, name='questions_daily_data'),
    path('weekly/', question.weekly, name='weekly'),
    path('weekly/data/', question.questions_weekly_data, name='questions_weekly_data'),
    path('monthly/', question.monthly, name='monthly'),
    path('monthly/data/', question.questions_monthly_data, name='questions_monthly_data'),
    path('yearly/', question.yearly, name='yearly'),
    path('yearly/data/', question.questions_yearly_data, name='questions_yearly_data'),
    path('category/', question.HomePageView.as_view(), name='category'),
    path('api/category/data/', question.ChartData.as_view(), name="category-data"),
    path('creation-follower/', creation_follower.CreationFollowerChartView.as_view(), name='creation-follower'),
    path('api/creation-follower/data/', creation_follower.CreationFollowerChartData.as_view(), name="creation-follower-data"),
    path('reply-delay/', reply_delay.ReplyDelayChartView.as_view(), name='reply-delay'),
    path('api/reply_delay/data/', reply_delay.ReplyDelayChartData.as_view(), name="reply-delay-data"),

]