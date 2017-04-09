import json
import os

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from analyzer.forms import ScrapeForm
from analyzer.models import Amazon_Scrape, Amazon_Analyse


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
            q = Amazon_Scrape()
            q.fun(url)
            print('Url is', url)

            return HttpResponseRedirect('/reports')

        product_url = request.POST.get('search_query', "")
        print("-------------" + product_url + "---------------")
        return HttpResponse("<h1>Error occurred while analyzing : " + product_url + "</h1>")

    def reports(request):
        print("analyse : get function")
        q = Amazon_Analyse()
        score, data, comments, comments_sentiment = q.analyse_class()

        with open('amazon_data.json') as data_file:
            f = json.load(data_file)

        title = f['name']

        # getting image data
        imageFile = open(os.getcwd() + "/imageData.txt", "r")
        base64 = imageFile.read()

        form = ScrapeForm()
        specs_list = []
        p = []
        f = open('specs.txt')
        for line in f:
            p.append(line)
        # print p
        try:
            for i in range(0, len(p), 2):
                specs_list.append((p[i], p[i + 1]))

            print(specs_list)
        except Exception:
            specs_list = []
            form = ""

        positive = 0
        negative = 0
        for i, emotion in enumerate(comments_sentiment):
            if emotion == 1:
                positive += 1
            else:
                negative += 1

        comments_list={}
        for spec in list(comments):
            comments_list[spec] = comments[spec]

        return render(request, 'result.html',
                      {'data': data,
                       'comments': comments_list,
                       'title': title,
                       'image': base64,
                       'form': form,
                       'specs_list': specs_list,
                       'total_reviews': positive + negative,
                       'score': score,
                       'positive_sentiment': positive,
                       'negative_sentiment': negative,
                       }
                      )
