import httplib2
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

url = 'http://www.amazon.in/TomTom-Spark-1RE0-002-01-Fitness-Watch/dp/B01BF8V7Z2/ref=sr_1_1?ie=UTF8' \
      '&qid=1486800606&sr=8-1'

###amazon###
h = httplib2.Http()
resp, content = h.request(url, 'GET')

soup = BeautifulSoup(content, 'lxml', parse_only=SoupStrainer('a'))
link = soup.find('a', {'class': 'a-link-emphasis a-text-bold'})
print(link['href'] + "\n")

resp, response = h.request(link['href'], 'GET')
soup = BeautifulSoup(content, 'lxml')
tag = soup.find('div', id='a-page') \
    .find_all('div')[1] \
    .find('div')
