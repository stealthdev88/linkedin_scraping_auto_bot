from flask import Flask ,request, jsonify
from flask import render_template
import sqlite3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from scraper import seamless_scraper
from scraper_send import start_send_thread, stop_send_thread
from scraper_receive import start_receive_thread, stop_receive_thread
from scraper_mailchimp import start_mailchimp_thread, stop_mailchimp_thread

import pandas as pd
import os
import random


app = Flask(__name__)
items = []

@app.route("/")
def index():    
    data = {'pagetitle': 'automation contacts', 'header': "Custom Automation",'isloggedin': True}
    get_db_connection();
   
    return render_template('index.html', data=data)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    return conn    

def create_user(result_data):
    print("==================================================")
    print(result_data)
    conn = get_db_connection()
    url = f"{result_data[0]['domain']}"
    if(get_user(url) == 0):
        for entry in result_data:
            url = f"{entry['domain']}"
            company_name = f"{entry['company']}"
            name = f"{entry['name']}"
            print("name:" + name)
            role = f"{entry['role']}"
            linkedIn = f"{entry['linkedin']}"
            email1 = f"{entry['email1']}"
            conn.execute('INSERT INTO tb_email (url,company_name,name, role,linkedin,email1) VALUES (?,?,?,?,?,?)', (url,company_name, name,role,linkedIn,email1));
            conn.commit()
    conn.close()      

def get_user(company_url):
    conn = get_db_connection()
    counts = conn.execute('SELECT count(*) FROM tb_email WHERE url = ?', (company_url,)).fetchone()
    conn.close()
    return counts[0]

def get_data():
    conn = get_db_connection()
    all_data = conn.execute('SELECT * FROM tb_email').fetchall()
    conn.close()
    users_list = [dict(data) for data in all_data]
    
    return users_list
  
@app.route('/start_contact', methods=['POST'])
def start_contact():
    url_data = request.json.get('url_data')
    title_search = request.json.get('title_search')
    count = get_user(url_data)
    result_data = ""
    print(count)
    if count == 0:
        result_data = seamless_scraper(url_data,title_search)
    
    if len(result_data) == 0:        
        return jsonify({"results": result_data, "message": "No Results Found! Click ok"})
    else:       
       create_user(result_data)
       send_data = get_data()
       return jsonify({"results": send_data, "message": "success"})

@app.route('/db_data_show', methods=['POST'])
def db_data_show():
    send_data = get_data()
    return jsonify({"results": send_data, "message": "success"})

@app.route('/send_message', methods=['POST'])
def start_send_message():
    flag = request.json.get('flag')
    print(flag)
    if flag :
        result = start_send_thread()
        return jsonify({"results": result})
    else :
        result = stop_send_thread()
        return jsonify({"results": result})

@app.route('/receive_message', methods=['POST'])
def receive_message():
    flag = request.json.get('flag')
    print(flag)
    if flag :
        result = start_receive_thread()
        return jsonify({"results": result})
    else :
        result = stop_receive_thread()
        return jsonify({"results": result})

@app.route('/mailchimp_check', methods=['POST'])
def mailchimp_check():
    flag = request.json.get('flag')
    print(flag)
    if flag :
        result = start_mailchimp_thread()
        return jsonify({"results": result})
    else :
        result = stop_mailchimp_thread()
        return jsonify({"results": result})

if __name__ == "__main__":
    app.run(host='0.0.0.0')