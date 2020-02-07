import urllib.request
from bs4 import BeautifulSoup as bs

url = 'https://patents.google.com/?q=test&oq=test'
html = urllib.request.urlopen(url).read()
soup = bs(html, 'html.parser')

print(soup)