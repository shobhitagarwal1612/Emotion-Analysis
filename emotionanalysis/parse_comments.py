import httplib2
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

html_doc = open('html_doc.html')

# soup = BeautifulSoup(html_doc, 'html.parser')
# print(soup.prettify())
# for a in soup.find_all('a'):
#     print(a.string)

###amazon###
h = httplib2.Http(".cache")
resp, content = h.request('http://www.amazon.in/TomTom-Spark-1RE0-002-01-Fitness-Watch/dp/B01BF8V7Z2/ref=sr_1_1?ie=UTF8'
                          '&qid=1486800606&sr=8-1', 'GET')

soup = BeautifulSoup(content, 'lxml', parse_only=SoupStrainer('a'))
# print((soup.prettify()))
link = soup.find('a', {'class': 'a-link-emphasis a-text-bold'})
print(link['href'] + "\n")

resp, response = h.request(link['href'], 'GET')
# print(resp)
soup = BeautifulSoup(content, 'lxml')
tag = soup.find('div', id='a-page') \
    .find_all('div')[1] \
    .find('div')

# print(tag)
# for span in soup.select('span.a-color-base'):
#     print(span.text)
