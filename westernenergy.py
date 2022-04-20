from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import datetime
import re
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from pyvirtualdisplay import Display
from selenium import webdriver
display = Display(visible=0, size=(800, 600))
display.start()
import os


def offline_website_selenium(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")


    # Event Name
    event_name = driver.find_element_by_tag_name('title').get_property('text')
    event_name = event_name.split("|")[0]

    month = driver.find_element_by_xpath("//p[contains(@class, 'month')]").text
    date = driver.find_element_by_xpath("//p[contains(@class, 'date')]").text
    try:
        d1, d2 = date.split('-')
        start_end_date = f'{d1} {month} 2022'
        regex = re.sub('[\,/,-, ,*]', '/', start_end_date)
        format = "%d/%b/%Y"
        formatted_date_1 = datetime.datetime.strptime(regex,format).date()
        start_end_date = f'{d2} {month} 2022'
        regex = re.sub('[\,/,-, ,*]', '/', start_end_date)
        formatted_date_2 = datetime.datetime.strptime(regex,format).date()
    except Exception as e:
        try:
            d1 = date
            start_end_date = f'{d1} {month} 2022'
            regex = re.sub('[\,/,-, ,*]', '/', start_end_date)
            format = "%d/%b/%Y"
            formatted_date_1 = datetime.datetime.strptime(regex,format).date()
            # print(formatted_date_1)
        except:
            month, date = month.split(" ")
            start_end_date = f'{date} {month} 2022'
            regex = re.sub('[\,/,-, ,*]', '/', start_end_date)
            format = "%d/%b/%Y"
            formatted_date_1 = datetime.datetime.strptime(regex,format).date()
            # print(formatted_date_1)

    # content
    info = driver.find_element_by_xpath("//meta[@property='og:description']").get_property("content")


    time = soup.find_all("p",attrs={'class':'program-schedule-time'})
    # time = driver.find_elements_by_xpath("//p[@class='program-schedule-time']")
    title = soup.find_all("p", attrs={'class': 'program-schedule-title'})
    desc = soup.find_all("div", attrs={'class':'program-schedule-content'})
    timeList = []
    titleList = []
    descList = []
    maxNumber = max(len(time), len(title), len(desc))
    for i in range(maxNumber):
        try:
            timeList.append(time[i].text)
        except:
            timeList.append("")
        try:
            titleList.append(title[i].text)
        except:
            titleList.append("")
        try:
            descList.append(desc[i].text)
        except:
            descList.append("")
    Agenda_list = []
    for i in range(len(timeList)):
        startTime = timeList[i].split('-')[0]
        endTime = timeList[i].split('-')[-1].replace("\n", "")
        sep = ':'
        time = {}
        regex1 = re.findall('\d+',startTime)
        regex2 = re.findall('\d+',endTime)
        time["Start_time"] = startTime
        time["end_time"] = endTime
        time['day'] = ''
        time['title'] = titleList[i]
        time['desc'] = descList[i]
        Agenda_list.append(time)

    # # Speaker List
    speakers_tag = soup.find_all("div",attrs={'class':'large-3 medium-6 small-12 columns' })
    speaker_list = []

    for speaker in speakers_tag:
        x = speaker.findAll('h2')
        y = speaker.findAll('h5')
        for i in range(len(x)):
            s = {}
            s["name"] = x[i].text
            s["title"] = y[i].text
            speaker_list.append(s)
    print(speaker_list)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    city = soup.find_all("div",attrs={'class':'large-6 columns' })
    # city = driver.find_element_by_id("comp-kvg5h1y91").find_element_by_tag_name("span").text
    text = ""
    for i in city:
        if "program location" in i.text.lower():
            text += i.text
    venue_list = text.split("\n\n")
    for i in venue_list:
            if "program location" in i.lower():
                if "virtual" in i.lower():
                    online_event = 1
                    venue = None
                    break
                else:
                    online_event = 0
                    venue  = i[i.lower().find("location")+9:].replace("\n", " ")
                    x = re.findall('\d\d\d\d\d', venue)[0]
                    venue = venue[:venue.find(x)+5]
                    break
            else:
                venue = None

    if venue is not None:
        try:
            print(venue)
            driver.get("https://google.co.in/search?q="+venue)
            map = driver.find_element_by_xpath('//img[@class="lu-fs"]')
            map.click()
            google_url = (driver.current_url)
        except:
            google_url = ""
    else:
        google_url = ""
    # print(venue)
    print(google_url)

    #Ticket List
    price = driver.find_elements_by_xpath('/html/body/div[1]/section[3]/div/div/div/div/div[1]/div/div[2]/div[2]/ul[1]/li[2]/p[1]')
    price_list = []
    for i in price:
        i = i.text
        if ("Member:" in i) or ("Regular:" in i) or ('Conference' in i):
            text_list = i.split("\n")
            for j in text_list:
                if ("Member:" in j) or ("Regular:" in j) or ('Conference' in i):
                    p_dict = {}
                    p_dict["Type"] = 'Paid'
                    print(j)
                    price = j[j.find('$'):].split('\n')[0].replace(',', '')
                    print(price)
                    p_dict["Price"] = re.findall("\d+", price)[0]
                    p_dict["Currency"] = "$"
                    price_list.append(p_dict)
                    print(price_list)

    


    day = soup.find_all("h4", attrs={'style' : 'margin-top: 1rem;'})
    Time_list = []
    for i in range(len(day)):
        new_dict= {}
        d = day[i].text
        print(d)
        x = day[i].find_next("h4")
        if x is not None:
            endTime = x.find_previous("p", attrs={'class' : 'program-schedule-time'}).text
        new_dict["Type"] = 'general'
        startTime = (day[i].find_next("p", attrs={'class' : 'program-schedule-time'}).text)
        new_dict["Start_time"] = startTime.split('-')[0]
        new_dict["end_time"] = endTime.split('-')[-1].replace("\n", "")
        new_dict["timezone"] = ""
        new_dict['Days'] =  "All"
        Time_list.append(new_dict)
        print(Time_list) 

    contactmail = driver.find_elements_by_xpath('//div[@class="large-6 columns"]')
    for i in contactmail:
        x = i.find_elements_by_tag_name('a')
        for j in x:
            mail = str(j.get_attribute('href'))
            if 'mail' in mail:
                mailId = mail.split(':')[-1]
                print(mailId) 

    df={}
    df["scrappedUrl"]=url
    df["eventname"]=event_name
    df["startdate"]=str(formatted_date_1)
    if 'formatted_date_2' in locals():
        df["enddate"]=str(formatted_date_2)
    else:
        df["enddate"]=str(formatted_date_1)

    if 'Time_list' in locals():
        df["timing"] = json.dumps(Time_list)
    else:
        df["timing"] = None
    df["eventinfo"] = info
    if 'price_list' in locals():
        df["ticketlist"]= json.dumps(price_list)
    else:
        df["ticketlist"]= None

    df["orgProfile"] = None
    df["orgName"] = None
    df["orgweb"] = None
    df["logo"]=None
    df["sponsor"]=None
    if 'Agenda_list' in locals():
        df["agendalist"]= json.dumps(Agenda_list)
    else:
        df["agendalist"]= None
  
    df["type"] = None
    df["category"] = None
    df["city"] = None
    df["country"] = None
    if 'venue' in locals():
        df["venue"] = venue
    else:
        df["venue"] = None
    df["event_website"] = url
    df["googlePlaceUrl"] = google_url
    if 'mailId' in locals():
        df["ContactMail"] = mailId
    else:
        df["ContactMail"] = None

    if 'speaker_list' in locals():
        df["Speakerlist"] = json.dumps(speaker_list)
    else:
        df["Speakerlist"] = None
    if 'online_event' in locals():
        df["online_event"] = online_event
    else:
        df["online_event"] = None

    df=pd.DataFrame([df])
    df=df.replace({'\'': ''}, regex=True)
    return df

def convert_to_csv(data):
# if file does not exist write header 
    if not os.path.isfile('westernenergy_1.csv'):
        data.to_csv('westernenergy_1.csv', sep=",", index=False)
    else: # else it exists so append without writing the header
        data.to_csv('westernenergy_1.csv', mode='a', index=False, header=False)
    # data.to_csv('offline_example_5-4-2022_selenium.csv', mode= 'a')



for i in range(1,4):
    url = f'https://www.westernenergy.org/programs/page/{i}/'
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

    soup=BeautifulSoup(driver.page_source,"html.parser")

    print('perent:',url)
    for i in soup.find_all("section",attrs={"class":"program-wrapper"})[0].find_all("a"):
        print("child url:",i['href'])
        data = offline_website_selenium(i['href'])
        convert_to_csv(data)
