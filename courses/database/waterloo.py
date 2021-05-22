import json
import requests
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get("WATERLOO")


def get_term():
    url = "https://openapi.data.uwaterloo.ca/v3/Terms/current"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))["termCode"]


def get_courses(term=get_term()):
    url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{term}"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    print(response.status_code, response.content)


print(get_courses())