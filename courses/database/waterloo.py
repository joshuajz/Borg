import json
import requests
import os
from dotenv import dotenv_values
from methods.database import Courses_DB

cwd = os.getcwd().split("/")

while ".env" not in os.listdir():
    try:
        os.chdir("..")
        if os.getcwd() == "/" or os.getcwd() == "\\":
            break

    except:
        print(
            "Error moving directories.  Make sure you haven't renamed the folder that Borg resides in."
        )

cfg = dotenv_values(".env")
api_key = cfg["waterloo_api"]
if api_key is None:
    print("Error.  Can not find .env file and therefore there is no Waterloo API key.")


async def get_term():
    url = "https://openapi.data.uwaterloo.ca/v3/Terms/current"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))["termCode"]
    else:
        return False


async def get_courses():
    term = await get_term()
    url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{term}"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return False


# Get more detailed information -> not used right now.
async def get_course(course, term=get_term()):
    url = f"https://openapi.data.uwaterloo.ca/v3/Courses/{term}/{course}"
    header = {"x-api-key": api_key}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return False


async def pull_values():
    courses = await get_courses()
    db = await Courses_DB("waterloo")

    def pull_numbers(string):
        final = ""
        for s in string:
            if s.isnumeric():
                final += s
        return final

    in_database = await db.fetch_courses()

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

        course_code = course["subjectCode"] + course["catalogNumber"]

        if course_code in in_database:
            continue

        await db.add_course(
            course_code,
            course_number,
            course["subjectCode"],
            course["title"],
            course["description"],
            requirements=course["requirementsDescription"],
            campus=campus,
        )

    print("Finished Waterloo Courses.")
