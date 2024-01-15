import requests
import json
import random
# import fastapi
from fastapi import FastAPI
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")
# Prepare headers
headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + API_KEY,
    "Content-Type": "application/json"
}

app = FastAPI()


@app.get("/job-options/")
async def job_options(title: str):
    n = 5
    job_ids = search_jobs(title=title)
    # find 10 reandom job ids
    random.shuffle(job_ids)
    job_ids = job_ids[:n]
    job_profiles = []
    for job_id in job_ids:
        job_profile = collect_job(job_id)
        job_profiles.append(job_profile)
    print("returning job profiles")
    return {"jobs": job_profiles}


@app.get("/job-profile/")
async def job_profile(job_id: int):
    job_profile = collect_job(job_id)
    print(json.dumps(job_profile, indent=4, sort_keys=True))
    print("returning job profile")
    return {"job": job_profile}


def search_jobs(created_at_gte="2023-09-01 00:00:00", created_at_lte=None, last_updated_gte=None,
                last_updated_lte=None, title=None, keyword_description=None,
                employment_type=None, location=None, company_id=None, company_name=None,
                company_domain=None, company_exact_website=None,
                company_professional_network_url=None, deleted=None,
                application_active='true', country='United States', industry=None):

    url = "https://api.coresignal.com/cdapi/v1/linkedin/job/search/filter"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Constructing the payload dynamically
    payload = {k: v for k, v in locals().items() if v is not None and k !=
               'api_key' and k != 'url' and k != 'headers'}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        # Assuming the response JSON structure contains a list of job IDs
        job_ids = response.json()
        return job_ids
    else:
        raise Exception(f"Error in API request: {response.status_code}")


def collect_job(job_id):
    # Execute GET request
    url = "https://api.coresignal.com/cdapi/v1/linkedin/job/collect/"
    response = requests.get(url + str(job_id), headers=headers)
    if response.status_code == 200:
        job_profile = response.json()
    else:
        print("Error:", response.status_code)
        return
    return job_profile
