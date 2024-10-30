import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import os
import random

def seamless_scraper(company_name, titles_string):
  login_url = 'https://login.seamless.ai/login'
  mail_address = "steve@paymentspayce.com"
  user_password = "PaymentSpayce#1"

  trimmed_titles = [title.strip() for title in titles_string.split(',')]

  chrome_options = webdriver.ChromeOptions()
  # chrome_options.add_argument('--proxy-server=https://stevekaralekas:ngL7sx8TnY@115.167.26.50:50100')

  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)  # {{ edit_2 }}
  driver.maximize_window()

  driver.get(login_url)

  try:   
    shadow_host = driver.find_element(By.TAG_NAME, 'aside')
    driver.execute_script("arguments[0].setAttribute('style', 'display:none;')", shadow_host)
  except Exception as e:
    print(f"Cookies modal not found or could not be clicked: {e}")

  driver.find_element(By.ID, "rs-:r0:").send_keys(mail_address)
  time.sleep(1)
  driver.find_element(By.ID, "rs-:r1:").send_keys(user_password)
  time.sleep(3)
  driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
  time.sleep(30)

  button = driver.find_element(By.XPATH, "//*[@id='SearchFiltersList']//div[@role='listitem']//a[@role='button']")  # {{ edit_7 }}
  button.click()

  input_element = driver.find_element(By.XPATH, "//*[@id='SearchFiltersList']//div[@role='listitem']//input")
  input_element.send_keys(company_name)
  input_element.send_keys(Keys.ENTER)
  part_company_name = company_name.split(".")
  if len(part_company_name) > 1 :
    input_element.send_keys(part_company_name[0])
    input_element.send_keys(Keys.ENTER)

  button = driver.find_element(By.XPATH, "//*[@id='SearchFiltersList']//div[@role='listitem'][3]//a[@role='button']")  # {{ edit_7 }}
  button.click()

  input_element = driver.find_element(By.XPATH, "//*[@id='SearchFiltersList']//div[@role='listitem'][3]//input")
 
  for title in trimmed_titles:  # {{ edit_3 }}  # Iterate through each title
    input_element.send_keys(title)
    input_element.send_keys(Keys.ENTER)

  time.sleep(1)
  print("find search")
  search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
  search_button.click()

  time.sleep(5)

  try:
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Find All')]")
    button.click()
    time.sleep(3)
    while True:
      try:
        span_element = driver.find_element(By.XPATH, "//table//span[text()='Researching']")
        print("Found span:", span_element.text)
        time.sleep(10)
        driver.refresh()
      except Exception as e:
        print(f"Error finding span by text: {e}")
        break
  except Exception as e:
    print(f"Error clicking button by text: {e}")

  results = []
  try :
    table_element = driver.find_element(By.XPATH, "//table[@role='table']")
    # print(table_element.get_attribute('outerHTML'))
    soup = BeautifulSoup(table_element.get_attribute('outerHTML'), 'html.parser')
    time.sleep(5)
    table = soup.find('table').find_all('tr')
    for row in range(len(table)):
      if 'th' in [ tag.name for tag in table[row] ]:
        continue
      
      item = {}
      try:
        item_row = table[row].find_all('td')
        item['domain'] = company_name
        item['company'] = item_row[2].find('div').find('div').text
        print('company' + item['company'])
        print(len(item_row))
        item['name'] = item_row[1].find('div').find('div').text          
        print('name' + item['name'])
        item['role'] = item_row[1].find('div').find('div').next_sibling.text
        print('role' + item['role'])
        print(item_row[1].find('div').find('div').next_sibling)
        item['linkedin'] = item_row[1].find('a')['href']
        if item_row[3].find('div').find('div').text == "Add Email" :
          item['email1'] = ""
        else :  
          item['email1'] = item_row[3].find('div').find('div').text
        

        results.append(item)
      except Exception as e:
        print(f"table data get error: {e}")
        break
  except Exception as e:
    print(f"table not found: {e}")

  return results
