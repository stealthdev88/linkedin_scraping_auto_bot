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

date_format = "%Y-%m-%d %H:%M:%S"
candendly_link = "candendly_link_url"
stop_send_thread_flag = False
send_thread = None

def add_days_to_date(original_date, days_to_add):
    new_date = original_date + timedelta(days=days_to_add)  # {{ edit_2 }}
    return new_date

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    return conn    

def linkedin_scraper(website2_url, message_text, driver):
  print("linkedin_scraper called url:" + website2_url + " message:" + message_text)
  result_flag = True
  driver.execute_script("window.open('" + website2_url + "')")
  time.sleep(5)
  driver.switch_to.window(driver.window_handles[1])
  print("find button") 
  time.sleep(10)
  try:
    accept_button = driver.find_element(By.XPATH, "//button[span[text()='Accept']]")
    accept_button.click()  # Click the button
    print("Clicked the Accept button.")
  except Exception as e:
    print(f"An error occurred: {e}")

  try:
    print("find button1") 
    # find more button and click it
    pending_buttons = driver.find_elements(By.XPATH, "//button[span[text()='Pending']]")
   
    print("find button2") 
    if len(pending_buttons) > 0 :
      result_flag = False
    else:
      print("find button2-1")
      find_buttons = driver.find_elements(By.XPATH, "//button[span[text()='More']]")
      print(len(pending_buttons))
      find_buttons[1].click()
      print("find button3") 
      # Using XPath to find the button
      connect_buttons = driver.find_elements(By.XPATH, "//span[text()='Connect']")
      connect_buttons[1].click()
      print("find button4") 
      time.sleep(2)
      note_button = driver.find_element(By.XPATH, "//button[span[text()='Add a note']]")
      note_button.click()
      print("find button5") 
      time.sleep(5)

      textarea = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//textarea[@id='custom-message']"))
      )
      textarea.clear()
      textarea.send_keys(message_text)

      # send_button = driver.find_element(By.XPATH, "//button[span[text()='Send']]")
      # send_button.click()

      time.sleep(5)
  except Exception as e:
    print(f"An error occurred: {e}") 
    result_flag = False

  driver.close()  
  driver.switch_to.window(driver.window_handles[0])

  return result_flag

def linkedin_send_thread():
  global stop_send_thread_flag
  print("Send Thread: starting")
  login_url = 'https://www.linkedin.com/feed/?trk=guest_homepage-basic_nav-header-signin'
  proxy_username = "stevekaralekas"
  proxy_password = "ngL7sx8TnY"
  proxy_address = "115.167.26.50:50101"

  proxy_string = f"socks5://{proxy_username}:{proxy_password}@{proxy_address}"

  proxy_settings = Proxy()
  proxy_settings.proxy_type = ProxyType.MANUAL
  proxy_settings.http_proxy = proxy_string
  proxy_settings.ssl_proxy = proxy_string


  capabilities = webdriver.DesiredCapabilities.CHROME.copy()
  proxy_settings.add_to_capabilities(capabilities)

  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument('--ignore-certificate-errors')
  chrome_options.add_argument("--disable-webrtc")
  # chrome_options.add_argument("--headless")  # Enables headless mode for Selenium
  chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
  chrome_options.add_argument("--no-sandbox")    # Bypass OS security model
  chrome_options.add_argument("--window-size=1920x1080")  # Set a specific window size
  chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # Mimic a regular browser

  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options, desired_capabilities=capabilities)  # {{ edit_5 }}
  driver.maximize_window()

  driver.get("https://www.linkedin.com") 
  driver.add_cookie(
    {
      'name': "li_at", 
      'value': "AQEDAU4EMCkEUt0-AAABkpr9etgAAAGSvwn-2E4AkWTb4ouKvHx1PRS7XZfCY5SftUNU8f4r--EHRIk97DcTuOypvB9370xH3HE7Bzh-7er68btkOZRu0OmnGvQhToLCQK1qfGC-mEBz7ZwHhJ-5upGx", 
      'domain': "www.linkedin.com"
    })
  driver.get(login_url)
  # time.sleep(6000)   # Let it run for a while      
  # Locate the "Accept" button using XPath
  try:
    accept_button = driver.find_element(By.XPATH, "//button[span[text()='Accept']]")
    accept_button.click()  # Click the button
    print("Clicked the Accept button.")
  except Exception as e:
    print(f"An error occurred: {e}")

  while not stop_send_thread_flag:
    print("Send Thread: working...")
    conn = get_db_connection()
    row = conn.execute('SELECT id, linkedin, req_time, req_flag, name, type FROM tb_email WHERE req_flag < 7 and res_flag = 0 order by req_flag, req_time').fetchone()
    if row is not None:
      # Process the row
      id = row[0]
      linkedin = row[1]
      req_time = row[2]
      req_flag = row[3]
      name = row[4]
      type = row[5]
      print("Row found:", linkedin)
    else:
      print("No available row found.")
      time.sleep(60)   # Let it run for a while      
      continue

    message_data = None
    if req_flag == 0 :
      if type != 'p' :
        message_data = conn.execute('SELECT message, days FROM tb_message WHERE level = ? and type = ?', (req_flag+1, "m")).fetchone()
      else :
        message_data = conn.execute('SELECT message, days FROM tb_message WHERE level = ? and type = ?', (req_flag+1, "p")).fetchone()
    else :
      message_data = conn.execute('SELECT message, days FROM tb_message WHERE level = ?', (req_flag+1,)).fetchone()
    print(message_data)
    if message_data is not None:
      message = message_data[0]
      days = message_data[1]
      print(message_data)
      send_flag = True
      send_message = message.replace('[name]', name).replace('[Calendly Link]', candendly_link)

      if req_flag != 0 :
        original_date = datetime.strptime(req_time, date_format)
        next_date = add_days_to_date(original_date, days)
        if datetime.now() > next_date :
          send_flag = True
        else:
          send_flag = False

      if send_flag:
        if linkedin_scraper(linkedin, send_message, driver) :
          sql_update_query = "Update tb_email set req_flag = " + str(req_flag+1) + ", req_time = '" + datetime.now().strftime(date_format) + "' where id = " + str(id)
          print(sql_update_query)
          cursor = conn.cursor()
          cursor.execute(sql_update_query)
          conn.commit()
          cursor.close()
      else : 
        time.sleep(60)
    else :
      time.sleep(60)
    conn.close()
  driver.close()    
  print("Send Thread: finishing")


def start_send_thread():
  global send_thread, stop_send_thread_flag
  if send_thread is None or not send_thread.is_alive():
    stop_send_thread_flag = False  # Reset the stop flag
    send_thread = threading.Thread(target=linkedin_send_thread)
    send_thread.start()
    print("Send Thread started.")
    return True
  else :
    return False

def stop_send_thread():
  global stop_send_thread_flag
  stop_send_thread_flag = True  # Signal the thread to stop
  if send_thread is not None:
    send_thread.join()  # Wait for the thread to finish
    print("Send Thread stopped.")
    return True
  else :
    return False

# Example usage
start_send_thread()  # Start the thread
time.sleep(600)   # Let the thread run for a while
stop_send_thread()  # Stop the thread

# Optionally, you can restart the thread
start_send_thread()  # Restart the thread
time.sleep(600)   # Let it run for a while
stop_send_thread()  # Stop the thread again



