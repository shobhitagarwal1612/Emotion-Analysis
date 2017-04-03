from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt


class IndexView(View):
    http_method_names = [u'get', u'post']

    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')

    @csrf_exempt
    def fetchComments(request):
        product_url = request.POST.get('search_query', "")
        print("-------------" + product_url + "---------------")
        return HttpResponse("Comments parsed " + product_url)
