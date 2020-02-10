#import urllib.request
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.chrome.options import Options

import os
import pyperclip

baseurl = 'https://patents.google.com/?q='
plusurl = input('Search : ')
url = baseurl + quote_plus(plusurl)

chromeOptions = Options()

current_path = os.path.dirname(os.path.realpath(__file__))
download_path = current_path + r'\searchResults'
if not os.path.exists(download_path):
    os.makedirs(download_path)

prefs = {'profile.default_content_settings.popups': 0,
         'download.default_directory': download_path,
         'download.prompt_for_download': False,
         'directory_upgrade': True,
         'safebrowsing.enabled': True,
         'safebrowsing.disable_download_protection': True}

chromeOptions.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chrome_options=chromeOptions)

driver.get(url)

try:
    element = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.ID, 'count'))
    )
finally:
    driver.find_element_by_css_selector('#count > div > span > a').click()
    #driver.quit()
