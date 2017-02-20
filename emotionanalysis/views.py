from django.shortcuts import render
from django.views import View


class IndexView(View):
    http_method_names = [u'get', u'post']

    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
