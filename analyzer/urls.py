from django.conf.urls import url

from analyzer.views import IndexView

app_name = 'analyzer'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^analyze/$', IndexView.scrape, name='analyze'),
    url(r'^reports/$', IndexView.reports, name='reports'),
    url(r'^newspec/$', IndexView.analyse_newspec, name='newspec')
]
