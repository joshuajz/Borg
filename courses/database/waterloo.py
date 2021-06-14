import json
import requests
import os
from dotenv import load_dotenv
from methods.database import database_connection

cwd = os.getcwd().split("/")
while cwd[-1] != "Borg":
    try:
        os.chdir("..")
    except:
        print(
            "Error moving directories.  Make sure you haven't renamed the folder that Borg resides in."
        )

load_dotenv()
api_key = os.environ.get("waterloo_api")


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


async def pull_values(courses=get_courses()):
    db, cursor = await database_connection()

    def pull_numbers(string):
        final = ""
        for s in string:
            if s.isnumeric():
                final += s
        return final

    cursor.execute("SELECT code FROM courses WHERE school = 'waterloo'")
    in_database = [i[0] for i in cursor.fetchall()]

    for course in courses:
        campus = None
        course_number = course["catalogNumber"]

        if course_number is None:
            continue

        if course_number[-1].upper() == "B":
            continue
        elif course_number[-1].upper() == "A":
            course_number = course_number[0:-1]
        elif course_number[-1].upper() == "R":
            campus = "Renison"
            course_number = course_number[0:-1]
        elif course_number[-1].upper() == "*":
            course_number = None
        else:
            course_number = pull_numbers(course_number)
            if len(str(course_number)) == 0:
                course_number = None

        course_code = course["subjectCode"] + "-" + course["catalogNumber"]

        if course_code in in_database:
            continue

        cursor.execute(
            "INSERT INTO courses(school, code, number, department, name, description, requirements, campus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                "waterloo",
                course_code,
                course_number,
                course["subjectCode"],
                course["title"],
                course["description"],
                course["requirementsDescription"],
                campus,
            ),
        )

    print("Finished Waterloo Courses.")
