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
from selenium.webdriver.common.proxy import Proxy, ProxyType 
from datetime import datetime, timedelta
import sqlite3
import random
import threading
import time


stop_mailchimp_thread_flag = False
mailchimp_thread = None
mailchimp_email = "stevekaralekas@gmail.com"
mailchimp_pass = "PaymemtSpayve#1"

def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row  # Allows us to access columns by name
  return conn    

def wait_for_specific_url(driver, target_url, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: d.current_url == target_url)  # {{ edit_1 }}

def mailchimp_addcontent_thread():
  global stop_mailchimp_thread_flag
  print("mailchimp Thread: starting")


  capabilities = webdriver.DesiredCapabilities.CHROME.copy()
  
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument('--ignore-certificate-errors')
  chrome_options.add_argument("--disable-webrtc")  # Disable WebRTC

  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
  driver.maximize_window()

  driver.get("https://login.mailchimp.com/?locale=en") 
  print("waiting for login client...")
  time.sleep(5)
  cookies_element = driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
  cookies_element.click()

  username_element = driver.find_element(By.XPATH, "//input[@id='username']")
  username_element.send_keys(mailchimp_email)

  pass_element = driver.find_element(By.XPATH, "//input[@id='password']")
  pass_element.send_keys(mailchimp_pass)

  submit_element = driver.find_element(By.XPATH, "//button[@id='submit-btn']")
  submit_element.click()
  time.sleep(5)

  send_code_button = driver.find_element(By.XPATH, "//a[@data-mc-el='sendTfaSms' and text()='Send code']")
  send_code_button.click()

  wait_for_specific_url(driver, "https://us17.admin.mailchimp.com/", 300)
  print("login success !!!!")

  while not stop_mailchimp_thread_flag:
    print("mailchimp Thread: working...")

    driver.get("https://us17.admin.mailchimp.com/audience/contacts/") 
    print("incoming add Content")
    conn = get_db_connection()
    row = conn.execute('select email1, name, id from tb_email where res_flag = 1').fetchone()
    if row is not None:
      email = row[0]
      name = row[1]
      id = row[2]
      print("mailchimp record row found")
      if email == "" :
        print("record email emptyed")
        continue;  
    else :
      print("mailchimp record row not found")
      time.sleep(10)
      continue
    time.sleep(2)

    try:
      add_button = driver.find_element(By.XPATH, "//button[span[text()='Add contacts']]")
      print(add_button.get_attribute('outerHTML'))
      add_button.click()
      print("Add contents button clicked----------1")

    except Exception as e:
      print(f"Error finding span by text: {e}")
      break
    
    time.sleep(2)
    link_element = driver.find_element(By.XPATH, "//a[div[text()='Add a single contact']]")
    href_value = link_element.get_attribute("href")
    id_value = href_value.split('=')[1]
    print("id_value: " + id_value)
    driver.get("https://us17.admin.mailchimp.com/audience/add-contact?id=" + id_value)

    form_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//main//form"))
    )
    
    print("form", form_element.get_attribute('form_element'))

    input_elements = form_element.find_elements(By.XPATH, ".//input")

    input_elements[0].send_keys(email)    
    print("email input:", input_elements[0].get_attribute('outerHTML'))
    input_elements[1].send_keys(name)
    print("name input:", input_elements[1].get_attribute('outerHTML'))
    
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "optin-confirm"))
    )
    print("checkbox input:", checkbox.get_attribute('outerHTML'))

    if not checkbox.is_selected():
      checkbox.click()

    checkbox1 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "mc-admin-SMSPHONE-ack"))
    )
    
    if not checkbox1.is_selected():
      checkbox2.click()

    checkbox2 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "update-existing"))
    )
    
    if not checkbox2.is_selected():
      checkbox2.click()


    add_contact_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Add contact']]"))
    )

    add_contact_button.click()
    print("add contact button clicked")
    sql_update_query = "Update tb_email set res_flag = 2 where id=?"
    cursor = conn.cursor()
    cursor.execute(sql_update_query, (id,))
    conn.commit()
    print("update tb_email database")
    conn.close()
    

  driver.quit()
  print("mailchimp Thread: finishing")
  

def start_mailchimp_thread():
  global mailchimp_thread, stop_mailchimp_thread_flag
  if mailchimp_thread is None or not mailchimp_thread.is_alive():
    stop_mailchimp_thread_flag = False  # Reset the stop flag
    mailchimp_thread = threading.Thread(target=mailchimp_addcontent_thread)
    mailchimp_thread.start()
    print("mailchimp Thread started.")

# Function to stop the thread
def stop_mailchimp_thread():
  global stop_mailchimp_thread_flag
  stop_mailchimp_thread_flag = True  # Signal the thread to stop
  if mailchimp_thread is not None:
    mailchimp_thread.join()  # Wait for the thread to finish
    print("Thread stopped.")

# # Example usage
# start_mailchimp_thread()  # Start the thread
# time.sleep(600)   # Let the thread run for a while
# stop_mailchimp_thread()  # Stop the thread

# # Optionally, you can restart the thread
# start_mailchimp_thread()  # Restart the thread
# time.sleep(600)   # Let it run for a while
# stop_mailchimp_thread()  # Stop the thread again

