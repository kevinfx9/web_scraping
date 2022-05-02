from selenium import webdriver
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
import datetime
import re
import warnings
from pyvirtualdisplay import Display
warnings.filterwarnings("ignore", category=DeprecationWarning)
from selenium.webdriver.remote.remote_connection import LOGGER
import re
from datetime import datetime

def date_format(regex):
    regex=re.sub('January','Jan',regex)
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
    regex=re.sub(' ','/',regex)
    format = "%d/%b/%Y"
    date= datetime.strptime(regex,format).date()
    return date

def scrape_ihs_1(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver1 = webdriver.Chrome(ChromeDriverManager().install())
    driver2 = webdriver.Chrome(ChromeDriverManager().install())

    new1=url+'overview.html'
    new2=url+'webinar-schedule.html'
    
    driver.get(url)
    driver1.get(new1)
    driver2.get(new2)

    # soup=BeautifulSoup(driver1.page_source,"html.parser")
    
    display = Display(visible=0, size=(1920,1080))
    display.start()

    df={}

    df["Scrapped URL"]=url

    event=driver1.find_element_by_xpath('//*[@id="main-content"]/div[1]/section/div/div/div/div').text
    event=event.splitlines()
    event_name=event[0]
    df["Event Name"]=event_name

    # date=driver2.find_element_by_xpath('//*[@id="main-content"]/section[2]/div/div/table[1]').find_elements_by_tag_name('tr')
    date=driver2.find_element_by_xpath('//*[@id="main-content"]/section[2]/div[2]/div/div/table').find_elements_by_tag_name('tr')
    d=[]
    for i in date:
        n=i.find_elements_by_tag_name('td')
        ds=[]
        for j in n:
            ds.append(j.text)
        d.append(ds)

    year=driver2.find_element_by_css_selector('span.short-detail').text
    year=year.split(" ")
    year=year[5]

    sdate=d[1][0]+" "+year
    edate=d[-1][0]+" "+year
    df["Start Date"]=date_format(sdate)
    df["End Date"]=date_format(edate)

    try:
        time=driver1.find_element_by_xpath('//*[@id="event_side_speaker_0"]/div[2]/div').find_element_by_tag_name('strong')
        df["Timing"]=time.text.splitlines()[2]
    except:
        time=driver1.find_element_by_xpath('//*[@id="event_side_speaker_0"]/div[2]/div/p[2]/strong').text
        time=re.sub("Time:","",time)
        df["Timing"]=time
    
    # info=driver1.find_element_by_css_selector('div.single-event').find_element_by_tag_name('p').text
    info=driver1.find_element_by_xpath('//*[@id="event_side_speaker_0"]/div[1]/p[2]').text
    df["Event Info"]=info

    df["Ticket List"]=None

    df["Org Profile"]=None

    org_name='IHS Markit'
    df["Org Name"]=org_name
    org_web='https://ihsmarkit.com/events/index.html'
    df["Org Website"]=org_web

    df["Logo"]=None
    df["Sponsors"]=None

    df["Agenda"]=json.dumps(d[1:])

    type=driver.find_element_by_css_selector('span.value').text
    df["Type"]=type

    category=driver.find_element_by_xpath('//*[@id="resultsContent"]/li[1]/article/div[2]/div[2]/span[2]').text
    df["Category"]=category

    event_type=driver.find_element_by_xpath('//*[@id="resultsContent"]/li[1]/article/div[2]/div[3]/span[2]').text

    if event_type=='Virtual':
        df["City"]=None
        df["Country"]=None
        df["Venue"]=None
    else:
        pass

    website=url
    df["Event Website"]=website

    if event_type=='Virtual':
        df["Google Place"]=None
    else:
        pass

    df["Contact Mail"]=None

    try:
        speaker=driver1.find_element_by_css_selector('div.expert_grid').find_elements_by_css_selector('div.item')
        list=[]
        for s in speaker:
            s=s.find_element_by_css_selector('div.expert-title').find_element_by_tag_name('h4').text
            list.append(s)
        df["Speaker List"]=json.dumps(list)
    except:
        df["Speaker List"]=None
    
    if event_type=='Virtual':
        df["Online Event"]=1

    df=pd.DataFrame([df])
    df=df.replace({'\'': ''}, regex=True)
    df.to_csv('ihsmarkit.csv', mode='a',sep=",",index=False, header=False)

def scrape_ihs_2(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver1 = webdriver.Chrome(ChromeDriverManager().install())
    driver2 = webdriver.Chrome(ChromeDriverManager().install())

    new1=url+'overview.html'
    new2=url+'webinar-schedule.html'
    
    driver.get(url)
    driver1.get(new1)
    driver2.get(new2)
    
    display = Display(visible=0, size=(1920,1080))
    display.start()

    df={}

    df["Scrapped URL"]=url

    try:
        event=driver1.find_element_by_xpath('//*[@id="main-content"]/div[1]/section/div/div/div/div').text
        event=event.splitlines()
        event_name=event[0]
        df["Event Name"]=event_name
    except:
        df["Event Name"]=None

    date=driver1.find_element_by_css_selector('span.short-detail').text
    date=date.split(" ")
    try:
        year=date[5]
        sdate=date[0]+" "+date[1]+" "+year
        edate=date[3]+" "+date[4]+" "+year

        df["Start Date"]=date_format(sdate)
        df["End Date"]=date_format(edate)

        time=date[6]+" "+date[7]+" "+date[8]
        df["Timing"]=time
    except:
        year=date[2]
        sdate=date[0]+" "+date[1]+" "+year
        edate=date[0]+" "+date[1]+" "+year

        df["Start Date"]=date_format(sdate)
        df["End Date"]=date_format(edate)

        time=date[3]+" "+date[4]+" "+date[5]
        df["Timing"]=time

    info=driver1.find_element_by_xpath('//*[@id="main-content"]/div[2]/section/div/div/p[1]').text
    df["Event Info"]=info

    df["Ticket List"]=None

    df["Org Profile"]=None

    org_name='IHS Markit'
    df["Org Name"]=org_name
    org_web='https://ihsmarkit.com/events/index.html'
    df["Org Website"]=org_web

    df["Logo"]=None
    df["Sponsors"]=None

    agenda=driver1.find_element_by_xpath('//*[@id="main-content"]/div[2]/section/div/div').find_elements_by_tag_name('p')
    list=[]
    for a in agenda:
        a=re.sub("Click Here","",a.text)
        list.append(a)
    df["Agenda"]=json.dumps(list[2:])

    type=driver.find_element_by_css_selector('span.value').text
    df["Type"]=type

    category=driver.find_element_by_xpath('//*[@id="resultsContent"]/li[1]/article/div[2]/div[2]/span[2]').text
    df["Category"]=category

    event_type=driver.find_element_by_xpath('//*[@id="resultsContent"]/li[1]/article/div[2]/div[3]/span[2]').text

    if event_type=='Virtual':
        df["City"]=None
        df["Country"]=None
        df["Venue"]=None
    else:
        pass

    website=url
    df["Event Website"]=website

    if event_type=='Virtual':
        df["Google Place"]=None
    else:
        gplace=driver1.find_element_by_xpath('//*[@id="fullscreen"]')
        print(gplace)

    df["Contact Mail"]=None
    
    try:
        speaker=driver1.find_element_by_css_selector('div.expert_grid').find_elements_by_css_selector('div.item')
        list=[]
        for s in speaker:
            s=s.find_element_by_css_selector('div.expert-title').find_element_by_tag_name('h4').text
            list.append(s)
        df["Speaker List"]=json.dumps(list)
    except:
        df["Speaker List"]=None
    
    if event_type=='Virtual':
        df["Online Event"]=1

    df=pd.DataFrame([df])
    df=df.replace({'\'': ''}, regex=True)
    df.to_csv('ihsmarkit.csv', mode='a',sep=",",index=False, header=False)

def scrape_ihs_3(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver1 = webdriver.Chrome(ChromeDriverManager().install())
    driver2 = webdriver.Chrome(ChromeDriverManager().install())
    driver3 = webdriver.Chrome(ChromeDriverManager().install())

    new1=url+'overview.html'
    new2=url+'agenda.html'
    new3=url+'speakers.html'
    
    driver.get(url)
    driver1.get(new1)
    driver2.get(new2)
    driver3.get(new3)
    
    display = Display(visible=0, size=(1920,1080))
    display.start()

    df={}

    df["Scrapped URL"]=url

    try:
        event=driver1.find_element_by_xpath('//*[@id="main-content"]/div[1]/section/div/div/div/div').text
        event=event.splitlines()
        event_name=event[0]
        df["Event Name"]=event_name
    except:
        df["Event Name"]=None

    date=driver1.find_element_by_css_selector('span.short-detail').text
    date=date.split(" ")
    try:
        year=date[5]
        sdate=date[0]+" "+date[1]+" "+year
        edate=date[3]+" "+date[4]+" "+year

        df["Start Date"]=date_format(sdate)
        df["End Date"]=date_format(edate)
    except:
        year=date[2]
        sdate=date[0]+" "+date[1]+" "+year
        edate=date[0]+" "+date[1]+" "+year

        df["Start Date"]=date_format(sdate)
        df["End Date"]=date_format(edate)
    
    time=driver2.find_element_by_xpath('//*[@id="main-content"]/section[2]/div/div[2]/div[2]/section[2]').find_elements_by_css_selector('div.sessions')
    list=[]
    for t in time:
        t=t.find_elements_by_tag_name('span')
        slist=[]
        for s in t:
            slist.append(s.text)
        list.append(slist)
        
    df["Timing"]=list[0][0]+" - "+list[-1][0]
    
    info=driver1.find_element_by_xpath('//*[@id="event_side_speaker_0"]/div[1]/p[2]').text
    df["Event Info"]=info
    
    df["Ticket List"]=None

    df["Org Profile"]=None

    org_name='IHS Markit'
    df["Org Name"]=org_name
    org_web='https://ihsmarkit.com/events/index.html'
    df["Org Website"]=org_web

    df["Logo"]=None
    df["Sponsors"]=None

    df["Agenda"]=json.dumps(list)
    
    type='Upcoming in-person event'
    df["Type"]=type

    category='IHS Markit Briefing'
    df["Category"]=category

    event_type='In-Person'

    df["City"]="Singapore"
    df["Country"]="Singapore"
    df["Venue"]="The Fullerton Hotel Singapore"

    website=url
    df["Event Website"]=website

    if event_type=='Virtual':
        df["Google Place"]=None
    else:
        gplace='https://www.google.com/maps/place/The+Fullerton+Hotel+Singapore/@1.2863532,103.8530671,15z/data=!4m2!3m1!1s0x0:0x41c12c50babf70d0?sa=X&ved=2ahUKEwiq9r_oj-j2AhU-QUEAHcITCoQQ_BJ6BAg1EAU'
        df["Google Place"]=gplace

    df["Contact Mail"]=None
    
    try:
        speaker=driver3.find_element_by_css_selector('div.grid-12').find_elements_by_css_selector('div.grid-2 speaker-info')
        list=[]
        for s in speaker:
            s=s.find_element_by_css_selector('div.speaker-content').find_element_by_css_selector('a.microsite-speaker play-icon modal').text
            list.append(s)
        df["Speaker List"]=json.dumps(list)
    except:
        df["Speaker List"]=None
    
    if event_type=='Virtual':
        df["Online Event"]=1
    else:
        df["Online Event"]=0

    df=pd.DataFrame([df])
    df=df.replace({'\'': ''}, regex=True)
    df.to_csv('ihsmarkit.csv', mode='a',sep=",",index=False, header=False)

scrape_ihs_1('https://ihsmarkit.com/events/2022-automotive-solution-webinar-series/')
scrape_ihs_2('https://ihsmarkit.com/events/q3-ilevel-whats-new/')
scrape_ihs_3('https://ihsmarkit.com/events/singapore-energy-briefing-2022/')