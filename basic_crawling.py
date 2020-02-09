#import urllib.request
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException

import pyperclip

baseurl = 'https://patents.google.com/?q='
plusurl = input('Search : ')
url = baseurl + quote_plus(plusurl)

driver = webdriver.Chrome()
driver.get(url)

try:
    element = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.ID, "count"))
    )
finally:
    driver.find_element_by_css_selector('#count > div > span > a').click()
    #driver.quit()
