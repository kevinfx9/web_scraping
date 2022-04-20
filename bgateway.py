from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import datetime
import requests
import re
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from pyvirtualdisplay import Display
from selenium import webdriver
display = Display(visible=0, size=(800, 600))
display.start()
from time import strptime 
import time
import os
from tqdm import tqdm
import streamlit as st


def offline_website_selenium(url):
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)
    print(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")



    # Event Name
    event_name = driver.find_element_by_xpath("//h1[@class='mt-5']")
    ev_name = event_name.text
    print(ev_name)


    event_info = driver.find_element_by_xpath("//div[@class='panel__copy pt-2 pb-2']")
    ev_info = event_info.text
    print(ev_info)
    
    date = driver.find_element_by_xpath('/html/body/div/div[3]/div[1]/div/div/div[2]/div/div[1]/p[1]')
    regex1 = re.findall('\d+',date.text)
    regex2 = re.findall('([A-Z].+?\s)', date.text)
    month = strptime(regex2[0][:3],'%b').tm_mon
    date = f'{regex1[-1]}/{month}/{regex1[0]}'
    print(date)

   
    Time_list = []
    ev_time = driver.find_element_by_xpath('/html/body/div/div[3]/div[1]/div/div/div[2]/div/div[1]/p[2]')
    new_dict = {}
    new_dict["Type"] = 'general'
    new_dict["Start_time"] = ev_time.text.split('-')[0]
    new_dict["end_time"] =  ev_time.text.split('-')[-1]
    new_dict["timezone"] = ""
    new_dict['Days'] = "All"
    Time_list.append(new_dict)
    print(Time_list)  

    venue = driver.find_element_by_xpath('/html/body/div/div[3]/div[1]/div/div/div[2]/div/div[1]/p[3]')
    online_event = driver.find_element_by_xpath('/html/body/div/div[3]/div[1]/div/div/div[2]/div/div[1]/p[4]')
    print(venue.text)
    if "webinar" in online_event.text.lower():
        online_event = 1
    else:
        online_event = 0
    print(online_event)
    # print(Essential_Info.text)


    
    contact_us = []
    social_dict = {}
    call = driver.find_element_by_xpath("//a[@class='footer__phoneno']")
    social_dict['call'] = call.text
    Socials = driver.find_elements_by_class_name('footer__social-item')
    for Social in Socials:
        social_link = Social.find_element_by_tag_name('a').get_attribute('href')
        if 'twitter' in social_link:
            social_dict['twitter'] = social_link
        if 'facebook' in social_link:
            social_dict['facebook'] = social_link
        if 'linkedin' in social_link:
            social_dict['linkedin'] = social_link
        if 'youtube' in social_link:
            social_dict['youtube'] = social_link
        if 'instagram' in social_link:
            social_dict['instagram'] = social_link
    contact_us.append(social_dict)
    print(contact_us)
    
    # driver.close()


    df={}
    df["scrappedUrl"]= url
    df["eventname"]= str(ev_name)
    df["startdate"]= str(date)
    df["enddate"]=str(date)

    if 'Time_list' in locals():
        df["timing"] = json.dumps(Time_list)
    else:
        df["timing"] = None

    df["eventinfo"]= str(ev_info)
    if 'price_list' in locals():
        df["ticketlist"]= None
    else:
        df["ticketlist"]= None

    df["orgProfile"] = None
    df["orgName"] = None
    df["orgweb"] = None
    df["logo"]=None
    df["sponsor"]=None
    if 'Agenda_list' in locals():
        df["agendalist"]= None
    else:
        df["agendalist"]= None

    df["type"] = None
    df["category"] = None
    df["city"] = None
    df["country"] = None
    if 'venue' in locals():
        df["venue"] = venue.text
    else:
        df["venue"] = None

    df["event_website"] = url
    df["googlePlaceUrl"] = None
    df['contact_us'] = json.dumps(contact_us)
    if 'speaker_list' in locals():
        df["Speakerlist"] = None
    else:
        df["Speakerlist"] = None

    if 'online_event' in locals():
        df["Online Event"] = online_event
    else:
        df["Online Event"] = None
    df=pd.DataFrame([df])
    df=df.replace({'\'': ''}, regex=True)
    return df
    
    # driver.close()


def convert_to_csv(data):
# if file does not exist write header 
    if not os.path.isfile('bgateway.csv'):
        data.to_csv('bgateway.csv', sep=",", index=False)
    else: # else it exists so append without writing the header
        data.to_csv('bgateway.csv', mode='a', index=False, header=False)

count = 0
url_list = {}
for i in tqdm(range(1,16)):
    url = f'https://www.bgateway.com/events/p{i}/'
    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)
    urls = driver.find_elements_by_class_name('col-10')
    for i in urls:
        x = (i.find_elements_by_tag_name('a'))
        for j in x:
            if "newsletter" not in j.get_attribute('href'):
                url_list[j.get_attribute('href')]=None
                print(j.get_attribute('href'))

                


for i in tqdm(url_list):
    data = offline_website_selenium(i)
    convert_to_csv(data)
    st.legacy_caching.clear_cache()
