import requests
import json
import random
# import fastapi
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from openai import OpenAI


load_dotenv()

JOBS_API_KEY = os.getenv("API_KEY")
PDF_API_KEY = os.getenv("PDF_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()


@app.get("/pdf-url/")
async def get_pdf_url(text: str):
    print("received text for conversion to pdf")
    # replace all ** with empty string
    text = text.replace("**", "")
    html = text_to_html(text)
    url = html_to_pdf_url(html)
    print("returning pdf url: " + url)
    return url


@app.get("/job-profiles/")
async def job_profiles(title: str):
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


def search_jobs(created_at_gte="2023-09-01 00:00:00", created_at_lte=None, last_updated_gte=None,
                last_updated_lte=None, title=None, keyword_description=None,
                employment_type=None, location=None, company_id=None, company_name=None,
                company_domain=None, company_exact_website=None,
                company_professional_network_url=None, deleted=None,
                application_active='true', country='United States', industry=None):

    url = "https://api.coresignal.com/cdapi/v1/linkedin/job/search/filter"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {JOBS_API_KEY}",
        "Content-Type": "application/json"
    }

    # Constructing the payload dynamically
    payload = {k: v for k, v in locals().items() if v is not None and k !=
               'api_key' and k != 'url' and k != 'headers'}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise requests.HTTPError(response.status_code)
        # Assuming the response JSON structure contains a list of job IDs
    job_ids = response.json()
    return job_ids


def collect_job(job_id):
    # Execute GET request
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {JOBS_API_KEY}",
        "Content-Type": "application/json"
    }
    url = "https://api.coresignal.com/cdapi/v1/linkedin/job/collect/"

    response = requests.get(url + str(job_id), headers=headers)
    if response.status_code != 200:
        raise requests.HTTPError(response.status_code)
    job_profile = response.json()

    return job_profile

# functions to convert html to text


def html_to_pdf_url(html):
    print("converting html to pdf")
    response = requests.post('https://api.pdfshift.io/v3/convert/pdf',
                             json={'source': html, 'filename': "resume.pdf"}, auth=('api', PDF_API_KEY))

    # Ensuring everything went fine:
    # raise_for_status will raise an exception if the status code is 4xx or 5xx
    if response.status_code != 200:
        raise requests.HTTPError(response.status_code)

    # print the response body
    json_response = response.json()
    return json_response['url']


# FUNCTIONs TO CONVERT TEXT TO HTML


def wrap_html_body(body):
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>Resume</title>
</head>
{body}
</html>"""

    return html_template


def text_to_html(text):
    print("converting text to html")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """Instructions to convert text to html: 
                Convert raw text of a resume to hierarchical HTML .
                Name should be h1.
                Any personal info should be an h4 on it's own line.
                Section headers should be an h2.
                Experience headers should be an h3 followed by details in an unordered list.
                All html will be wrapped only in a body tag.
                """
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model="gpt-4-1106-preview"
    )
    html = chat_completion.choices[0].message.content

    # reformat html
    html = html.replace("```html", "")
    html = html.replace("```", "")
    html = wrap_html_body(html)

    return html
