from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime,timedelta
import re
#locations = ["Qatar","United Kingdom","Teresina","João Pessoa","Aracaju","Berlin","Hamburg","Munich","Szolnok","Sopron","Stans"]
#locations = ["Qatar","United Kingdom","Teresina","João Pessoa","Aracaju","Berlin","Hamburg","Munich","Szolnok","Sopron","Stans","Dubai","France"]
locations = ["France","Qatar"]
def get_jobs(keyword, num_jobs):
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    # Initializing the webdriver
    global jobs_for_country
    jobs_for_country = []
    global jobs_for_countries
    jobs_for_countries = []
    global locations_sub
    locations_sub= []
    chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    chrome_options = Options()
    options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"]
    for option in options:
       chrome_options.add_argument(option)
    options = webdriver.ChromeOptions() 
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    for country in locations:
        jobs_for_country=[]
        url='https://www.glassdoor.com/Search/results.htm?keyword={}&locT=C&locName={}'.format(keyword.replace(' ','%20'),country)
        time.sleep(5)
        driver.get(url)
        # Let the page load. Change this number based on your internet speed.
        # Maybe add extra sleeping at the steps you need for more loading time. 
        time.sleep(3)
        print("the country is = ",country)
        #click on button search depends on job_title and city 
        try:
            driver.find_element(By.XPATH,'//span[@class="SVGInline d-flex white"]').click()
        except:
            pass
        #after loding the page we are clicking on "see all the jobs " button 
        time.sleep(5)
        try:
            driver.find_element(By.XPATH,'//span[@class="SVGInline css-1mgba7 css-1hjgaef"]').click()
        except:
            pass
        time.sleep(5)
        while len(jobs_for_country) < num_jobs: 
           job_buttons = driver.find_elements(By.XPATH,"//*[@id='MainCol']/div[1]/ul/li")
           # Going through each job url in this page
           job_buttons_href = driver.find_elements(By.XPATH,'//*[@id="MainCol"]/div[1]/ul/li/div[2]/a')
           #print("هون")
           number_of_all_page= driver.find_element(By.CLASS_NAME, "paginationFooter").text
           print("Now we in {} ".format(number_of_all_page)) 
           #for job in range(len(job_buttons)):
           for job_button in job_buttons:
               try:
                   print("Progress: {}".format("" + str(len(jobs_for_country)) + "/" + str(num_jobs)))
                   if len(jobs_for_country) >= num_jobs:
                       # When the number of jobs collected has reached the number we set. 
                       break
                   try:
                       job_button.click()
                   except:
                       pass
                   time.sleep(4)
                   try:
                       driver.find_element(By.XPATH,'//*[@id="JAModal"]/div/div[2]/span').click()
                   except NoSuchElementException:
                       pass
                   collected_successfully = False
                                  
                   while not collected_successfully:
                       try:
                           #time.sleep(10)
                           job_num=job_buttons.index(job_button)
                           company_name = driver.find_element(By.XPATH,'//div[@class="css-xuk5ye e1tk4kwz5"]').text
                           location = driver.find_element(By.XPATH,'.//div[@class="css-56kyx5 e1tk4kwz1"]').text
                           job_title = driver.find_element(By.XPATH,'.//div[@class="css-1j389vi e1tk4kwz2"]').text
                           job_id  = job_buttons[job_num].get_attribute("data-id")
                           job_url= job_buttons_href[job_num].get_attribute("href")
                           #job_description = driver.find_element(By.XPATH,'.//div[@class="jobDescriptionContent desc"]').text
                           collected_successfully = True
                       except:
                           collected_successfully = True
              
                   try:
                       Posted_Date=driver.find_element(By.XPATH,'//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[3]/div[2]/div[2]'.format(job_num+1)).text
                   except NoSuchElementException:
                       try:
                           Posted_Date=driver.find_element(By.XPATH,'//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[2]/div/div[2]'.format(job_num+1)).text
                       except:
                           Posted_Date="N/A"
                   now = datetime.now()
                   try:
                       exdate= [int(x) for x in re.findall(r'-?\d+\.?\d*',Posted_Date)][0]
                       Posted_Data_N=now.date() - timedelta(days=exdate)
                   except:
                       Posted_Data_N=now.date()
                       
                       
                       
                   #Click on "Show More" for extract full description                        
                   try:
                       driver.find_element(By.XPATH,'//div[@class="css-t3xrds e856ufb2"]').click()
                       job_description_full = driver.find_element(By.XPATH,'.//div[@class="jobDescriptionContent desc"]').text
                       #Extract job title from job description full 
                       lines=job_description_full.splitlines()
                       t=False
                       try:
                           for line in lines:
                               if re.search('Job Type',line):
                                   job_type = line.split(':')[1]
                                   t=True
                           if (t == False):
                               job_type='N/A'
                       except:
                           job_type='N/A'      
                   except NoSuchElementException:
                       job_description_full ="N/A" 
                       job_type='N/A'
                       pass                       
                   try:
                       salary_estimate = driver.find_element(By.XPATH,'//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[3]/div[1]/span'.format(job_num+1)).text
                       
                   except NoSuchElementException:
                       # You need to set a "not found value. It's important."
                       salary_estimate = 'N/A'
                  # print("the salary is =",salary_estimate) 
                   try: 
                       rating = driver.find_element(By.XPATH,'//*[@id="employerStats"]/div[1]/div[1]').text
                   except NoSuchElementException:
                       # You need to set a "not found value. It's important."
                       rating = 'N/A'
                   #Extract Current Date Collection from a Datetime Object
                   now = datetime.now()
                   current_date = now.date()
                   jobs_for_country.append({
                   "Country" : country,
                   "City" : location,
                   "JobId" :job_id,
                   "Source":"Glassdoor",
                   "CollectedDate":current_date,
                   "JobTitle" : job_title,
                   "CompanyName" : company_name,
                   "RatingNumber" : rating,
                  "PostedDate":Posted_Date,
                   "Salary" : salary_estimate,
                   "jobType" :job_type,
                   "JobURL" : job_url,
                   "ShortDiscribtion" : "N/A",
                   "fullJobDescribtion":job_description_full,
                   "Posted_Date_N":Posted_Data_N,
                   })                 
               except:
                   print("واطي ولاك")
                   break
           # Clicking on the "next page" button
           try:
               page = driver.find_element(By.XPATH,'//*[@id="MainCol"]/div[2]/div/div[2]').text
               page = page.split()
               if page[1]==page[3]:
                   break
               driver.find_element(By.CSS_SELECTOR,'[alt="next-icon"]').click()
               time.sleep(5)
           except:
               print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs_for_country)))
               break
        for i in jobs_for_country:
           jobs_for_countries.append(i)
    #This line converts the dictionary object into a pandas DataFrame.
    return pd.DataFrame(jobs_for_countries)
df=get_jobs('data',50)
df.to_excel("data_final.xlsx",index=True) 
     
