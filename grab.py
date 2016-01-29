
from BeautifulSoup import BeautifulSoup
import re
import os
import sys
import getopt
import urllib2
import zipfile
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def print_current_page(driver, filename):
    # now we got two windows, switch to the upfront one
    handles = driver.window_handles
    for handle in handles:
        if handle != driver.current_window_handle:
            driver.switch_to.window(handle)
        if driver.find_element_by_xpath("/html").get_attribute('id') == 'print-preview':
            break
    # wait for the page to come out
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "printPage"))
    )
    def execute(script, args):
        driver.execute('executePhantomScript', {'script': script, 'args' : args })

    driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
    # pageFormat = '''this.paperSize = {width: "780px", height: "1000px", margin: "10px"};'''
    pageFormat = '''this.paperSize = {format: "A3", margin: "1cm"};'''
    execute(pageFormat, [])
    render = 'this.render("{file_name}.pdf")'.format(file_name=filename)
    execute(render, [])
    print "\tSaved as %s.pdf" % filename


def get_driver():
    download_url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-macosx.zip"
    directory = '/tmp/'
    filename = 'phantomjs-2.1.1-macosx.zip'
    # if we don't have phantomjs in directory, we can download one and extract it
    if not os.path.isfile(directory + 'phantomjs-2.1.1-macosx/bin/phantomjs'):
        f = urllib2.urlopen(download_url)
        data = f.read()
        with open(directory + filename, "wb") as code:
            code.write(data)
        z = zipfile.ZipFile(directory + filename)
        z.extractall(directory)

    phantomjs = directory + 'phantomjs-2.1.1-macosx/bin/phantomjs'
    # mimic browser behavior
    desired_capabilities = dict(selenium.webdriver.DesiredCapabilities.PHANTOMJS)
    desired_capabilities["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")
    desired_capabilities["phantomjs.page.settings.Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"

    driver = selenium.webdriver.PhantomJS(executable_path=phantomjs, desired_capabilities=desired_capabilities)
    driver.set_window_size(1040, 985)
    return driver


def sign_in(driver, username, password):
    try:
        driver.find_element_by_id("pageContent_ucGlobalSignIn_divNonInstAnonimus")
        # sign in

        username_field = driver.find_element_by_id("txtEmail")
        password_field = driver.find_element_by_id("txtPassword")

        username_field.send_keys(username)
        password_field.send_keys(password)

        print ("Sign in with username and password.")
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ibSignIn"))
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


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hu:p:",["user=","pass="])
    except getopt.GetoptError:
        print 'grab.py -u <username> -p <password>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'grab.py -u <username> -p <password>'
            sys.exit()
        elif opt in ("-u", "--user"):
            username = arg
        elif opt in ("-p", "--pass"):
            password = arg

    base_url = "http://accessmedicine.mhmedical.com"
    url = base_url + "/book.aspx?bookID=1340"

    part_ids = get_part_ids(url)

    driver = get_driver()
    for i in range(len(part_ids)):
        print ("Going to Part %i: \n" % (i+1) + url + part_ids[i])

        # print part_soup.prettify()
        chapter_ids = get_chapter_ids(driver, url + part_ids[i])

        for j in range(len(chapter_ids)):

            driver.get(base_url + chapter_ids[j])
            print ("\tGoing to Part %i Chapter %i : \n\t" % (i+1, j+1) + base_url + chapter_ids[j])

            sign_in(driver, username, password)

            # Print chapter
            print_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "printTool"))
            )

            print_btn.click()

            print_current_page(driver, "part_%i_chapter_%i" % (i+1, j+1))

            # after printing, close current window
            driver.close()
            # switch window back
            driver.switch_to.window(driver.window_handles[0])


if __name__ == "__main__":
    main(sys.argv[1:])