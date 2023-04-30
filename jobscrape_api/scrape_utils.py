from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests


from datetime import datetime
import time
import json
import re


LanguageRegex = re.compile(r"\b(ada|algol|assembly|awk|bash|c(\+\+|#)?|cobol|css|html5|coffeescript|d|dart|delphi|elixir|elm|erlang|f#|fortran|go|groovy|haskell|html|java|javascript|julia|kotlin|lisp|lua|matlab|objective-c|ocaml|pascal|perl|php|powershell|prolog|python|r|ruby|rust|scala|scheme|scratch|shell|smalltalk|sql|swift|tcl|typescript|vb\.net|visual basic)\b", re.IGNORECASE)

FrameworkRegex = re.compile(r"\b(angular|aurelia|backbone\.js|react|spacy|beautifulsoup|bootstrap|bulma|cakephp|cherrypy|django|docker|ember\.js|express|fastapi|feathers\.js|flask|gatsby\.js|google cloud platform|grails|hapi\.js|hugo|ibm cloud|ionic|jest|jquery|koa|laravel|loopback|meteor|nestjs|next\.js|nuxt\.js|openstack|phoenix|polymer|pyramid|quasar|react\.js|redux|restify|ruby on rails|sails\.js|sanic|serverless|sinatra|selenium|socket|socket.io|strapi|styled-components|symfony|thunderbird|tornado|turboGears|uwsgi|vaadin|vue|vuex|wxWidgets|yarn|yesod|zepto)\b", re.IGNORECASE)

DatabaseRegex = re.compile(r"\b(cassandra|couchbase|couchdb|firebase|mongodb|ms sql|mysql|oracle|postgresql|redis|sqlite)\b", re.IGNORECASE)

SkillsRegex= re.compile(r"\b(amazon web services|aws|ansible|apache kafka|apache mesos|apache zookeeper|aws cloudformation|aws cloudwatch|aws lambda|azure|chef|circleci|cloudflare|docker|gcp|git|github|gitlab|jenkins|kubernetes|logstash|nginx|prometheus|puppet|redis|terraform|travis ci)\b", re.IGNORECASE)



def generate_glassdoor_url(job_name, page_number):
    base_url = "https://www.glassdoor.co.in/Job/india-"
    job_name = job_name.replace(" ", "-").lower()
    srch = f"IL.0,5_IN115_KO6,{len(job_name)+6}"
    ip = f"_IP{page_number}"
    return (f"{base_url}{job_name}-jobs-SRCH_{srch}{ip}.htm")



def fetch_jobs(url):
    html_content = []
    
    options = Options()
    options.add_argument("window-size=1920,1080")
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
    options.add_argument("accept-language=en-US,en;q=0.9")
    options.headless = True
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    driver.get(url)
#     driver.minimize_window()
    
    try:
        driver.find_element(By.XPATH,".//span[@class='SVGInline modal_closeIcon']").click()
        time.sleep(3)
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH, "//*[@id='JAModal']/div/div[2]/span/svg").click()
            time.sleep(3)
        except:
            time.sleep(3)
            pass
    
    done = False
    while not done:
        job_cards = driver.find_elements(By.XPATH,"//article[@id='MainCol']//ul/li[@data-adv-type='GENERAL']")
        for card in job_cards:
            card.click()
            time.sleep(1.5)

#             Closes the signup prompt
            try:
                driver.find_element(By.XPATH,".//span[@class='SVGInline modal_closeIcon']").click()
                time.sleep(3)
            except NoSuchElementException:
                time.sleep(3)
                pass

            html_content.append(driver.page_source)
            done = True

    return html_content



def process_skills(skills):
    # Get the list of languages
    languages = [lang[0] for lang in skills['languages']]
    
    # Remove empty strings and duplicates, ignoring case
    languages = list(set([lang.strip().lower() for lang in languages if lang.strip()]))
    
    # Combine the results into a dictionary
    return {
        'languages': languages,
        'frameworks': list(set([fr.strip().lower() for fr in skills['frameworks'] if fr.strip()])),
        'databases': list(set([db.strip().lower() for db in skills['databases'] if db.strip()])),
        'skills': list(set([skill.strip().lower() for skill in skills['skills'] if skill.strip()]))
}



def parse_html_to_json(html,count,keyword):
    soup = BeautifulSoup(html, 'html.parser')

    company_name = ""
    job_title = ""
    location = ""
    job_description = ""
    avg_base_pay_est = ""
    company_rating = ""
    company_link = ""
    time_since_posted = ""
    company_skills = "#N/A"

    try:
        company_name = soup.find('div', {'class': 'css-87uc0g e1tk4kwz1'}).text
    except:
        company_name = "#N/A"
    try:
        job_title = soup.find('div', {'class': 'css-1vg6q84 e1tk4kwz4'}).text
    except:
        job_title = "#N/A"
    try:
        location = soup.find('div', {'class': 'css-56kyx5 e1tk4kwz5'}).text
    except:
        location = "#N/A"  
    try:
        avg_base_pay_est = soup.find('div', {'class': 'css-1bluz6i e2u4hf13'}).text
    except:
        avg_base_pay_est = "#N/A"  
    try:
        time_since_posted = soup.find('div', {'class': 'd-flex align-items-end pl-std css-1vfumx3'}).text
    except:
        time_since_posted = "#N/A"    
    try:
        company_rating = soup.find('span', {'class': 'css-1m5m32b e1tk4kwz2'}).text
    except:
        company_rating = "#N/A"

    try:   
        job_description = soup.find('div', {'class': 'css-jrwyhi e856ufb5'}).text
#         job_description = soup.text
    
        language_matches = LanguageRegex.findall(job_description)
        framework_matches = FrameworkRegex.findall(job_description)
        database_matches = DatabaseRegex.findall(job_description)
        skills_matches = SkillsRegex.findall(job_description)

        company_skills = {
            'languages': language_matches,
            'frameworks': framework_matches,
            'databases': database_matches,
            'skills': skills_matches
        }
        company_skills = process_skills(company_skills)  
        ctr=0
        for i in company_skills.values():
            for j in i:
                ctr+=1
        if ctr==0:
            company_skills="#N/A"
        # debug here for 0 skills
    except:
        job_description = "#N/A"
    a_tags = soup.find_all('a', {'class': 'jobLink css-1rd3saf eigr9kq2'}) 
    try:
        company_link="https://glassdoor.co.in"+a_tags[count]["href"]
    except:
        company_link="#N/A"     
        

    # create dictionary object from extracted data
    job_data = {
        'keyword':keyword,
        'company_name': company_name,
        'job_title': job_title,
        'location': location,
        'job_description': job_description,
        'avg_base_pay_est': avg_base_pay_est,
        'company_rating': company_rating,
        'company_link': company_link,
        'time_since_posted': time_since_posted,
        'company_skills': company_skills
    }

    return json.dumps(job_data)



def remove_na_skills(json_data):
    for key in json_data:
        for job in json_data[key]:
            if job['company_skills'] == '#N/A':
                json_data[key].remove(job)
    return json_data



def scrape_job_results(JOB_NAME, NO_OF_PAGES, counter_var):
    print(f'Scraping Job-{counter_var} Started !')
    URLS = [generate_glassdoor_url(JOB_NAME, i) for i in range(1,NO_OF_PAGES+1)]

    json_list = []

    for url in URLS:
        html_content = fetch_jobs(url)
        for i in range(30):
            json_list.append(parse_html_to_json(html_content[i], i,JOB_NAME))
            
    print(f'Scraping Job-{counter_var} Ended !')
    
    return json_list



def SCRAPE_ALL_JOB_RESULTS(ScrapeJobsList, NO_OF_PAGES):
    final_json = {}
    counter_var = 0
    for job in ScrapeJobsList:
        counter_var += 1
        final_json[job] = scrape_job_results(job, NO_OF_PAGES, counter_var)
    return final_json



