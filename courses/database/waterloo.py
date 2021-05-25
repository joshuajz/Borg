import json
import requests
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get("WATERLOO")
db = sqlite3.connect("database.db")
cursor = db.cursor()


def get_term():
    url = "https://openapi.data.uwaterloo.ca/v3/Terms/current"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))["termCode"]
    else:
        return False


def get_courses(term=get_term()):
    url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{term}"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return False


# Get more detailed information -> not used right now.
def get_course(course, term=get_term()):
    url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{term}/{course}"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return False


def create_database():
    cursor.execute(
        """CREATE TABLE "waterloo" (
        "id" TEXT NOT NULL,
        "course_code" TEXT NOT NULL,
        "department" TEXT NOT NULL,
        "name" TEXT NOT NULL,
        "description" TEXT NOT NULL,
        "requirements" TEXT
    );"""
    )
    db.commit()


def pull_values(courses=get_courses()):

    current_courses = [
        i[0] for i in cursor.execute("SELECT id FROM waterloo").fetchall()
    ]

    for course in courses:
        course_id = course["catalogNumber"]
        if course_id is None:
            continue
        course_code = course["subjectCode"] + "-" + course_id

        if course_code in current_courses:
            continue

        cursor.execute(
            "INSERT INTO waterloo VALUES (?, ?, ?, ?, ?, ?)",
            (
                course_code,
                course["catalogNumber"],
                course["subjectCode"],
                course["title"],
                course["description"],
                course["requirementsDescription"],
            ),
        )
        db.commit()


try:
    create_database()
except:
    print("Database already created.")

pull_values()