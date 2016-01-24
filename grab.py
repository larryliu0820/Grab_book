import urllib2
from BeautifulSoup import BeautifulSoup
import re
from selenium import webdriver

base_url = "http://accessmedicine.mhmedical.com"
url = base_url + "/book.aspx?bookID=1340"

html_page = urllib2.urlopen(url)

soup = BeautifulSoup(html_page)
part_ids = [link.get('href') for link in soup.findAll('a', attrs={'class': "topLevelPart clearfix"})]

# header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# request = urllib2.Request(url + part_ids[0], headers=header)
# part_page = urllib2.urlopen(request)
print (url + part_ids[0])

driver = webdriver.Firefox()
driver.get(url + part_ids[0])
part_soup = BeautifulSoup(driver.page_source)
# print part_soup.prettify()
chapter_ids = [link.get('href') for link in part_soup.findAll('a', attrs={'href':re.compile("/content.aspx")})]

for id in chapter_ids:
    print id
# get all id for Parts

driver.get(base_url + chapter_ids[0])