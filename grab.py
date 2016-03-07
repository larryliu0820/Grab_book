#!/usr/bin/env python

import re
import os
import sys
import glob
import time
import stat
import urllib2
import zipfile
import getpass
import selenium
import HTMLParser

from BeautifulSoup import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def print_single_chapter(driver, filename):
    sign_in(driver)
    # Print chapter
    print_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "printTool"))
    )

    print_btn.click()

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
        driver.execute('executePhantomScript', {'script': script, 'args': args })

    driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
    # pageFormat = '''this.paperSize = {width: "780px", height: "1000px", margin: "10px"};'''
    pageFormat = '''this.paperSize = {format: "A3", margin: "1cm"};'''
    execute(pageFormat, [])
    render = 'this.render("{file_name}.pdf")'.format(file_name=filename)
    execute(render, [])
    print "\tSaved as %s.pdf" % filename

    # after printing, close current window
    driver.close()
    # switch window back
    driver.switch_to.window(driver.window_handles[0])


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
    st = os.stat(phantomjs)
    os.chmod(phantomjs, st.st_mode | stat.S_IEXEC)
    # mimic browser behavior
    desired_capabilities = dict(selenium.webdriver.DesiredCapabilities.PHANTOMJS)
    desired_capabilities["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36")
    desired_capabilities["phantomjs.page.settings.Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"

    driver = selenium.webdriver.PhantomJS(executable_path=phantomjs, desired_capabilities=desired_capabilities)
    driver.set_window_size(1040, 985)
    return driver


def sign_in(driver):
    try:
        driver.find_element_by_id("pageContent_ucGlobalSignIn_divNonInstAnonimus")
        # sign in
        username = raw_input('Username:')
        password = getpass.getpass(prompt='Password for %s: ' % username)

        username_field = driver.find_element_by_id("txtEmail")
        password_field = driver.find_element_by_id("txtPassword")

        username_field.send_keys(username)
        password_field.send_keys(password)

        print ("Signing in with username and password.")
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ibSignIn"))
        )
        elem.click()
    except selenium.common.exceptions.NoSuchElementException:
        pass


def get_parts(driver, url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source)
    part_elements = soup.findAll('a', attrs={'class': "topLevelPart clearfix"})
    part_elements = [elem for elem in part_elements if elem.findAll("span", {'class': 'part-title'})]

    return part_elements


def get_part_id(tag):
    span = tag.findAll("span",{'class': 'part-title'})[0]
    num = re.match('[a-z]+ ([a-z0-9]+)', span.text, flags=re.I).group(1)
    return num


def get_chapters(driver, url):

    driver.get(url)
    part_soup = BeautifulSoup(driver.page_source)

    while part_soup.findAll('div', attrs={'class': 'top-part'}):
        # print "DEBUG: get url"
        if part_soup.findAll('li', attrs={'class': 'subpart-chapter'}):
            # print "DEBUG: satisfied!"
            break
        driver.get(url)
        time.sleep(1)
        part_soup = BeautifulSoup(driver.page_source)

    chapter_elements = part_soup.findAll('a', attrs={'href':re.compile("^/*content.aspx")})
    # print("DEBUG In get_chapters: len(chapter_elements) = %i" % len(chapter_elements))
    chapter_elements = [elem for elem in chapter_elements if 'chapter' in elem.text.lower()]
    return chapter_elements


def get_href(tag):
    href = tag.get('href')
    if not href.startswith('/'):
        href = '/' + href
    return href


def get_chapter_id(tag):
    num = re.match('chapter ([a-z0-9]+):', tag.text, flags=re.I).group(1)
    return num


def print_multiple_chapters(driver, base_url, chapters, filename_prefix, start_num=0):
    chapter_ids = [get_chapter_id(chapter) for chapter in chapters]
    # print("DEBUG: In print_multiple_chapters, len(chapter_ids) = %i" % len(chapter_ids))
    postfix_urls = [get_href(chapter) for chapter in chapters]
    if start_num < chapter_ids[0]:
        start_num = 0
    elif start_num in chapter_ids:
        start_num = chapter_ids.index(start_num)
    for j in range(start_num, len(chapters)):
        driver.get(base_url + postfix_urls[j])

        print ("\tDownloading Chapter %s : \n\t" % chapter_ids[j] + base_url + postfix_urls[j])

        print_single_chapter(driver, filename_prefix + "chapter_%s" % chapter_ids[j])


def get_latest_file():
    part_num = 0
    chapter_num = 0
    for filename in glob.glob("*chapter_*.pdf"):
        chapter_num = filename.split('_')[-1].split('.')[0]
        if 'part' in filename:
            part_num = filename.split('_')[1]

    if chapter_num != 0:
        latest_file = 'chapter_%s' % chapter_num
        if part_num != 0:
            latest_file = ('part_%s_' % part_num) + latest_file
        resume_msg = 'Found %s.pdf in current directory, do you want to resume downloading from here? (Y/N): ' % latest_file
        resume = raw_input(resume_msg)
        if resume.lower() == 'n':
            part_num = 0
            chapter_num = 0

    return part_num, chapter_num


def get_book_name(driver):
    soup = BeautifulSoup(driver.page_source)
    header = soup.findAll("header", {'class': 'page-header'})[0]
    book_name = HTMLParser.HTMLParser().unescape(header.findAll('h1')[0].text)
    return book_name


def click_expand_all(driver):
    btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'expandall'))
        )
    btn.click()


def main(argv):

    url = argv[0]

    base_url = "http://accessmedicine.mhmedical.com"
    if base_url not in url:
        print('Error: only support books in %s' % base_url)
        sys.exit(1)

    print('Going to %s' % url)

    driver = get_driver()

    parts = get_parts(driver, url)

    # print out book name
    book_name = get_book_name(driver)

    print('Book name: ' + book_name)

    # find out breakpoint of last download task
    (part_num, chapter_num) = get_latest_file()

    if not parts:
        chapters = get_chapters(driver, url)
        if not chapters:
            print('Error: unable to find chapters in this page.')
            sys.exit(1)
        print_multiple_chapters(driver, base_url, chapters, "", start_num=chapter_num)
    else:
        part_ids = [get_part_id(part) for part in parts]
        if part_num < part_ids[0]:
            start_part = 0
        elif part_num in part_ids:
            start_part = part_ids.index(part_num)
        for i in range(start_part, len(part_ids)):
            print ("Downloading Part %i: \n" % part_ids[i] + url + parts[i].get('href'))
            # print part_soup.prettify()
            # print("DEBUG: url + parts[i].get('href') = " + parts[i].get('href'))
            chapters = get_chapters(driver, url + parts[i].get('href'))
            # print("DEBUG: len(chapters) = %i" % len(chapters))
            # resume downloading from last breakpoint
            start_num = chapter_num if i == start_part else 0
            print_multiple_chapters(driver, base_url, chapters, "part_%i_" % part_ids[i], start_num=start_num)


if __name__ == "__main__":
    main(sys.argv[1:])
