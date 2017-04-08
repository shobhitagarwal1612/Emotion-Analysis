from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from emotionanalysis.forms import ScrapeForm


class IndexView(View):
    http_method_names = [u'get', u'post']

    def get(self, request):
        form = ScrapeForm()
        return render(request, 'index.html', {'form': form})

    @csrf_exempt
    def scrape(request):
        # create a form instance and populate it with data from the request:
        form = ScrapeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # name_obj = Amazon_Url.objects.create(url=form.cleaned_data['url'] )
            url = form.cleaned_data['url']
            print('Url is received')
            # q = Amazon_Scrape()
            # q.fun(url)
            print('Url is', url)
            # return HttpResponseRedirect('/analyse/data/')

        product_url = request.POST.get('search_query', "")
        print("-------------" + product_url + "---------------")
        return HttpResponse("Comments parsed " + product_url)
