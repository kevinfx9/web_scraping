from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from csv import writer
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import datetime
import re
import json
from pyvirtualdisplay import Display

# Function for generation URL of different pages of same event.
def url_name_generator(name,id):
    src="https://www.researchfora.net/event/{}.php?id={}".format(name,id)
    return src

# Main function for scrapping the event website
def scrap_url(url,id):
    
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    
    display = Display(visible=0, size=(1920,1080))
    display.start()

    df={}

    df["Scrapped URL"]=url

    event_name=soup.find('div',class_='col-sm-12 col-md-12 bann').find('h3').text
    event_name=event_name.split('-')
    event_name=event_name[0]
    name=re.sub('/t','',event_name)
    df["Event Name"]=name

    date=driver.find_element_by_xpath('/html/body/div[4]/div/div/div[2]/div/table/tbody/tr[3]/td[2]').text
    regex=re.sub('January','Jan',date)
    regex=re.sub('February','Feb',regex)
    regex=re.sub('March','Mar',regex)
    regex=re.sub('April','Apr',regex)
    regex=re.sub("June",'Jun',regex)
    regex=re.sub('July','Jul',regex)
    regex=re.sub('August','Aug',regex)
    regex=re.sub('September','Sep',regex)
    regex=re.sub('October','Oct',regex)
    regex=re.sub('November','Nov',regex)
    regex=re.sub('December','Dec',regex)
    regex=re.sub('st','/',regex)
    regex=re.sub('nd','/',regex)
    regex=re.sub('rd','/',regex)
    regex=re.sub('th','/',regex)
    regex = re.sub('[\,/,-,*]', '/', regex)
    regex=re.sub(' ','',regex)
    format = "%d/%b/%Y"
    date = datetime.datetime.strptime(regex,format).date()
    df["Start Date"]=date
    df["End Date"]=date

    new = webdriver.Chrome(ChromeDriverManager().install())
    u=url_name_generator('agenda',id)
    new.get(u)
    t=[]
    time=new.find_element_by_class_name("tab-content").find_elements_by_tag_name('tbody')
    time=time[:7]
    for i in time:
        t.append(i.text)
    tlist=[]
    for i in t:
        i=i.split('\n')
        tlist.append(i)
    df["Timing"]=json.dumps(tlist)

    info=driver.find_element_by_class_name('intro_detail').find_element_by_tag_name('p').text
    df["Event Info"]=info

    df["Ticket List"]=None

    df["Org Profile"]=None

    org_name='Research Fora'
    df["Org Name"]=org_name
    org_web='https://www.researchfora.net/'
    df["Org Website"]=org_web

    df["Logo"]=None
    df["Sponsors"]=None
    df["Agenda"]=json.dumps(tlist)

    df["Type"]=None
    df["Category"]=None

    new = webdriver.Chrome(ChromeDriverManager().install())
    u=url_name_generator('venue',id)
    new.get(u)
    try:
        try:
            p=[]
            place=new.find_element_by_class_name('beadcrumb').find_element_by_tag_name('h1').find_elements_by_tag_name('p')
            for i in place:
                p.append(i.text)
            if len(p)<=1:
                df["City"]=p[0]
                df["Country"]=p[0]
                df["Venue"]=p[0]
            elif ',' in p[-1]:
                n=p[-1]
                n=n.split(',')
                df["City"]=n[-2]
                df["Country"]=n[-1]
                pc = ' '.join([str(elem) for elem in p])
                df["Venue"]=pc
            else:
                df["City"]=p[-2]
                df["Country"]=p[-1]
                pc = ' '.join([str(elem) for elem in p])
                df["Venue"]=pc
        except:
            place=new.find_element_by_class_name('beadcrumb').find_element_by_tag_name('h1').find_element_by_tag_name('p').text
            p=place.splitlines()
            if len(p)<=1:
                df["city"]=p[0]
                df["Country"]=p[0]
                df["Venue"]=p[0]
            elif ',' in p[-1]:
                n=p[-1]
                n=n.split(',')
                df["City"]=n[-2]
                df["Country"]=n[-1]
                pc = ' '.join([str(elem) for elem in p])
                df["Venue"]=pc
            else:
                df["City"]=p[-2]
                df["Country"]=p[-1]
                df["Venue"]=place
    except:
        try:
            p=[]
            place=new.find_element_by_class_name('beadcrumb').find_element_by_tag_name('h1').find_elements_by_tag_name('p')
            for i in place:
                p.append(i.text)
            df["City"]=None
            df["COuntry"]=None
            df["Venue"]=p
        except:
            place=new.find_element_by_class_name('beadcrumb').find_element_by_tag_name('h1').find_element_by_tag_name('p').text
            df["City"]=None
            df["Country"]=None
            df["Venue"]=place
    new.close()

    df["Event Website"]=url

    df["Google Place"]=None

    contact=driver.find_element_by_xpath('/html/body/header/div[1]/div/div/div[1]/p[2]/a').text
    df["Contact Mail"]=contact

    new = webdriver.Chrome(ChromeDriverManager().install())
    u=url_name_generator('committee',id)
    new.get(u)
    speaker=[]
    s=new.find_element_by_class_name('com').find_elements_by_tag_name('p')
    for i in s:
        speaker.append(i.text)
    df["Speaker List"]=json.dumps(speaker)
    new.close()

    df["Online Event"]=0

    df=pd.DataFrame([df])
    df=df.replace({'\'': ''}, regex=True)
    df.to_csv('research_fora.csv', mode='a',sep=",",index=False, header=False)

global temp
temp=0

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.researchfora.net/event.php?city=all')
soup=BeautifulSoup(driver.page_source,"html.parser")

count=0

urls=soup.find_all('div',class_='col-md-4 col-sm-6')
urls=urls[temp:]

for u in urls:
    if count>=50:
        break
    else:
        src='https://www.researchfora.net/'
        u=u.find('a')['href']
        src=src+u
        id=u.split('=')[-1]
        scrap_url(src,id)
        count=count+1
temp=temp+count