import json
import requests
import sqlite3
from db_connection import course_database_connection

# from courses.database.db_connection import course_database_connection

base = "https://api.qmulus.io/v1/courses/"
db, cursor = course_database_connection()


def get_info(offset=0):
    parameters = {
        "limit": "100",
        "offset": str(offset),
    }

    response = requests.get(base, params=parameters)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return False


def pull_values():
    offset = 0
    while True:
        info = get_info(offset)
        if info != False and len(info) != 0:
            place_info(info)
            offset += 100
        else:
            break


def place_info(items: list):
    for item in items:
        course_id = item["id"]
        course_code = item["course_code"]
        requirements = item["requirements"]

        if item["units"] == 0:
            continue

        if course_id[-1] == "B" or course_id[-1] == "A":
            course_id = course_id[0:-1]

        if course_code[-1] == "B" or course_code[-1] == "A":
            course_code = course_code[0:-1]

        if requirements == "":
            requirements = None

        try:
            course_code = int(course_code)
        except:
            continue

        cursor.execute(
            "INSERT INTO courses(school, code, number, department, name, description, requirements, academic_level, units) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                "queens",
                course_id,
                int(course_code),
                item["department"],
                item["course_name"],
                item["description"],
                requirements,
                item["academic_level"],
                item["units"],
            ),
        )


pull_values()