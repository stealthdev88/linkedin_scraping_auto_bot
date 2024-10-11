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
stop_receive_thread_flag = False
receive_thread = None

def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row  # Allows us to access columns by name
  return conn    

def linkedin_receive_thread():
  global stop_receive_thread_flag
  print("Receive Thread: starting")
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
  chrome_options.add_argument("--disable-webrtc")  # Disable WebRTC

  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options, desired_capabilities=capabilities)  # {{ edit_5 }}
  driver.maximize_window()


  driver.get("https://www.linkedin.com") 
  driver.add_cookie(
    {
      'name': "li_at", 
      'value': "AQEDAU4EMCkFAu3HAAABkme62rAAAAGSi8desE0AfpIY1olhyAOLa8FpoIkW5-N_ioMxx-o2RCAWZiN4xGHsna0tjo0VX1V6e7D-Fove76peqidfsQzm2GpHXqMtXwqy6oaBW8tHZs4B_LUlBRz_tnvQ", 
      'domain': "www.linkedin.com"
    })

  driver.get("https://www.linkedin.com/messaging/")
  while not stop_receive_thread_flag:
    print("Receive Thread: working...")
    time.sleep(5)
    conn = get_db_connection()
    unread_messages = driver.find_elements(By.CSS_SELECTOR, "li.msg-conversation-listitem .msg-conversation-card__convo-item-container--unread")
    name_list = []
    for message in unread_messages:
      participant_name = message.find_element(By.CSS_SELECTOR, ".msg-conversation-card__title-row").find_element(By.TAG_NAME, "h3").text
      timestamp = message.find_element(By.CSS_SELECTOR, ".msg-conversation-card__time-stamp").text
      print(f"Unread Message - Participant: {participant_name}, Time: {timestamp}")
      sql_update_query = "Update tb_email set res_flag = 1, res_time = ? where res_flag = 0 and name = ?"
      cursor = conn.cursor()
      cursor.execute(sql_update_query, (datetime.now().strftime(date_format), participant_name))
      conn.commit()
      name_list.append(participant_name)
    cursor.close()
    if len(name_list) > 0:
      conn = get_db_connection()
      for name in name_list:
        time.sleep(1000)
        user_info = conn.execute('SELECT name, email FROM tb_email WHERE name = ', (name,)).fetchone()
        chimp_name = user_info[0]
        chimp_email = user_info[1]
        conn.commit()
        if user_info is not None:
          chimp_name = user_info[0]
          chimp_email = user_info[1]
          print("User found:", chimp_name)
          # user info input
        else:
          print("No available user found.")
          time.sleep(60)   # Let it run for a while      
    conn.close()

  
  driver.close()
  print("Receive Thread: finishing")
  

def start_receive_thread():
  global receive_thread, stop_receive_thread_flag
  if receive_thread is None or not receive_thread.is_alive():
    stop_receive_thread_flag = False  # Reset the stop flag
    receive_thread = threading.Thread(target=linkedin_receive_thread)
    receive_thread.start()
    print("Receive Thread started.")
    return True
  else :
    return False

# Function to stop the thread
def stop_receive_thread():
  global stop_receive_thread_flag
  stop_receive_thread_flag = True  # Signal the thread to stop
  if receive_thread is not None:
    receive_thread.join()  # Wait for the thread to finish
    print("Thread stopped.")
    return True
  else :
    return False

# # Example usage
# start_receive_thread()  # Start the thread
# time.sleep(600)   # Let the thread run for a while
# stop_receive_thread()  # Stop the thread

# # Optionally, you can restart the thread
# start_receive_thread()  # Restart the thread
# time.sleep(600)   # Let it run for a while
# stop_receive_thread()  # Stop the thread again

