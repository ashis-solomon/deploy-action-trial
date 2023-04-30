import json
from datetime import datetime
from django.core.management.base import BaseCommand
from jobscrape_api.models import ScrapeResult, ScrapeJob
from core.settings import BASE_DIR
from jobscrape_api.scrape_utils import *

# ScrapeJobsList = ['React Developer', 'Data Analyst','Nodejs Developer', 'UI/UX Developer',\
#              'Django Developer', 'Flutter Developer', 'Java Developer',\
#              'Frontend Developer', 'Full-Stack Developer', 'DevOps Engineer',\
#              'Cloud Solutions Architect', 'Machine Learning Engineer',\
#              'Artificial Intelligence Specialist', 'Cybersecurity Analyst',\
#              'Network Engineer', 'Database Administrator', 'IT Support Specialist',\
#              'Python Developer', 'R&D Engineer']

class Command(BaseCommand):
    help = 'Reinitializes the ScrapeResult object after scraping the latest job postings.'

    def handle(self, *args, **kwargs):
        try:
            print(datetime.now())

            ScrapeJobsList = ScrapeJob.objects.values_list('job_name', flat=True)
            print(len(ScrapeJobsList))
            final_json = SCRAPE_ALL_JOB_RESULTS(ScrapeJobsList[:1], 1)
            print('POINT 1')
            temp_data = {}
            for key in final_json:
                    temp_data[key] = final_json[key]
                    for i,j in enumerate(final_json[key]):
                        temp_data[key][i] = json.loads(j)
                        
            final_json = temp_data
            final_json = remove_na_skills(final_json)
            print('POINT 2')
            
            ScrapeResult.objects.all().delete()
            print('POINT 3')

            print(final_json.keys())
            for job_name in final_json.keys():
                try:
                    print('POINT 4')
                    scrape_job = ScrapeJob.objects.get(job_name=job_name)
                    json_resp = {job_name: final_json[job_name]}
                    print('POINT 5')
                    scrape_result = ScrapeResult(job_name=scrape_job, json_resp=json_resp, date_created=datetime.now())
                    scrape_result.save()
                except Exception as e:
                    print(f"An error occurred: {e}")

            self.stdout.write(self.style.SUCCESS('ScrapeResult object reinitialized successfully'))
        except:
            self.stdout.write(self.style.ERROR('ScrapeResult object reinitialization FAILED!'))
