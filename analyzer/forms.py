from django import forms


class ScrapeForm(forms.Form):
    url = forms.URLField(label='Url of product', max_length=1000)
