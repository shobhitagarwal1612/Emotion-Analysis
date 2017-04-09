from django.conf.urls import url

from emotionanalysis.views import IndexView

app_name = 'analyzer'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^analyze/$', IndexView.scrape, name='analyze'),
    url(r'^reports/$', IndexView.reports, name='reports'),
]
