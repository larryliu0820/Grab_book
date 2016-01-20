import httplib2
import urllib2
from BeautifulSoup import BeautifulSoup
import re

url = "http://accessmedicine.mhmedical.com/book.aspx?bookID=1340"

html_page = urllib2.urlopen(url)
soup = BeautifulSoup(html_page)
for link in soup.findAll('a', attrs={'href': re.compile("content.aspx")}):
    print link.get('href')