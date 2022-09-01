import requests
from bs4 import BeautifulSoup

link = "https://onepiecechapters.com/chapters/4257/one-piece-chapter-1058"
	
def getdata(url):
	r = requests.get(url)
	return r.text

htmldata = getdata(link)	
soup = BeautifulSoup(htmldata, 'html.parser')
i = 1
for item in soup.find_all('img'):
    image = requests.get(soup.find_all('img')[i]['src'])
    file = open('{0}.png'.format(i), "wb")
    file.write(image.content)
    file.close()
    i += 1
