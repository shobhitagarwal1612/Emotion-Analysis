from django.conf.urls import url

from emotionanalysis.views import IndexView
from . import views

app_name = 'emotionanalysis'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
]
