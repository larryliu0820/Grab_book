import urllib2
from BeautifulSoup import BeautifulSoup
import re
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "http://accessmedicine.mhmedical.com"
url = base_url + "/book.aspx?bookID=1340"

html_page = urllib2.urlopen(url)

soup = BeautifulSoup(html_page)
part_ids = [link.get('href') for link in soup.findAll('a', attrs={'class': "topLevelPart clearfix"})]

# header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# request = urllib2.Request(url + part_ids[0], headers=header)
# part_page = urllib2.urlopen(request)
print ("Going to Part 1: \n" + url + part_ids[0])

chrome_driver = '/Users/larryliu/chromedriver'
# download_url = "http://chromedriver.storage.googleapis.com/2.20/chromedriver_mac32.zip"
driver = selenium.webdriver.Chrome(chrome_driver)
driver.get(url + part_ids[0])
part_soup = BeautifulSoup(driver.page_source)
# print part_soup.prettify()
chapter_ids = [link.get('href') for link in part_soup.findAll('a', attrs={'href':re.compile("/content.aspx")})]

# for id in chapter_ids:
#     print id

# get all id for Parts

driver.get(base_url + chapter_ids[0])
print ("Going to Part 1 Chapter 1: \n" + base_url + chapter_ids[0])

try:
    driver.find_element_by_id("pageContent_ucGlobalSignIn_divNonInstAnonimus")
    # sign in
    #username:dreamyyn
    #password:yuyannan

    username = driver.find_element_by_id("txtEmail")
    password = driver.find_element_by_id("txtPassword")

    username.send_keys("dreamyyn")
    password.send_keys("yuyannan")

    print ("Sign in with username and password.")
    elem = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "ibSignIn"))
    )
    elem.click()
except selenium.common.exceptions.NoSuchElementException as E:
    print ("Already signed in.")

# Print chapter
print_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "printTool"))
)
print_btn.click()