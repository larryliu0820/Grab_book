import urllib2
from BeautifulSoup import BeautifulSoup
import os
import stat
import zipfile
import re
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def print_current_page(driver, print_btn):
    print_btn.click()

    handles = driver.window_handles
    for handle in handles:
        if handle != driver.current_window_handle:
            driver.switch_to_window(handle)
        if driver.find_element_by_xpath("/html").get_attribute('id') == 'print-preview':
            break

    # Change destination to "Save PDF"
    change_btn = driver.find_element_by_class_name('destination-settings-change-button')
    change_btn.click()

    save_pdf_xpath = "/html/body/div[2]/div[1]/div[@class='lists']/div[@class='local-list']/div[1]/ul[1]/li[1]/span[1]/span[1]"
    save_pdf_elem = driver.find_element_by_xpath(save_pdf_xpath)
    save_pdf_elem.click()

    save_button = driver.find_element_by_xpath("//button[@class='print default']")
    save_button.click()


def get_driver():
    download_url = "http://chromedriver.storage.googleapis.com/2.20/chromedriver_mac32.zip"
    directory = '/tmp/'
    filename = 'chromedriver_mac32.zip'
    if os.environ['PATH'].find('chromedriver') is -1 and not os.path.isfile(directory + 'chromedriver'):
        f = urllib2.urlopen(download_url)
        data = f.read()
        with open(directory + filename, "wb") as code:
            code.write(data)
        z = zipfile.ZipFile(directory + filename)
        z.extractall(directory)
        st = os.stat(directory + 'chromedriver')
        os.chmod(directory + 'chromedriver', st.st_mode | stat.S_IEXEC)

    chrome_driver = directory + 'chromedriver'

    chromeOptions = selenium.webdriver.ChromeOptions()
    prefs = {"download.default_directory": "/tmp/"}
    chromeOptions.add_experimental_option("prefs",prefs)

    driver = selenium.webdriver.Chrome(executable_path=chrome_driver, chrome_options=chromeOptions)
    return driver


def sign_in(driver):
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


def get_part_ids(url):
    html_page = urllib2.urlopen(url)

    soup = BeautifulSoup(html_page)
    part_ids = [link.get('href') for link in soup.findAll('a', attrs={'class': "topLevelPart clearfix"})]
    return part_ids


def get_chapter_ids(driver, url):
    driver.get(url)

    part_soup = BeautifulSoup(driver.page_source)
    chapter_ids = [link.get('href') for link in part_soup.findAll('a', attrs={'href':re.compile("/content.aspx")})]
    return chapter_ids


def main():
    base_url = "http://accessmedicine.mhmedical.com"
    url = base_url + "/book.aspx?bookID=1340"

    part_ids = get_part_ids(url)

    driver = get_driver()
    # header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    # request = urllib2.Request(url + part_ids[0], headers=header)
    # part_page = urllib2.urlopen(request)
    print ("Going to Part 1: \n" + url + part_ids[0])

    # print part_soup.prettify()
    chapter_ids = get_chapter_ids(driver, url + part_ids[0])

    # for id in chapter_ids:
    #     print id

    # get all id for Parts
    # for i in range(len(chapter_ids)):
    for i in range(0,2):
        driver.get(base_url + chapter_ids[i])
        print ("Going to Part 1 Chapter %i : \n" % i + base_url + chapter_ids[i])

        sign_in(driver)

        # Print chapter
        print_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "printTool"))
        )

        print_current_page(driver, print_btn)


if __name__ == "__main__":
    main()