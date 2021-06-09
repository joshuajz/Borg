import json
import requests
import re
from methods.database import database_connection

base = "https://nikel.ml/api/courses"
db, cursor = database_connection()


def get_info(offset=0):
    parameters = {"limit": 100, "offset": offset}

    response = requests.get(base, params=parameters)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))["response"]
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


def place_info(courses: list):
    def split_code(code):
        r = re.compile("([a-zA-Z]+)([0-9]+)")
        m = r.match(code)
        return (code, m.group(2), m.group(1))

    def get_campus(code):
        end = code[-2::]
        if end[0] == "H":
            academic_units = 3
        else:
            academic_units = 3

        if end[1] == "1":
            campus = "UTSG"
        elif end[1] == "3":
            campus = "UTSC"
        elif end[1] == "5":
            campus = "UTM"
        return academic_units, campus

    """
    H1 - UTSG half year
    Y1 - UTSG full year

    H3 - UTSC half year
    Y3 - UTSC full year

    H5 - UTM half year
    Y5 - UTM full year
    """

    cursor.execute("SELECT code FROM courses WHERE school = 'uoft'")
    in_database = [i[0] for i in cursor.fetchall()]

    for course in courses:
        code = course["code"]
        if code is None:
            break
        try:
            academic_units, campus = get_campus(code)
        except:
            break

        code = course["code"]

        course_info = split_code(code)

        if course["code"] in in_database:
            continue

        requirements = ""
        if course["prerequisites"] == None:
            requirements += (
                "**Requirements**: None (Check the UofT website to be sure.\n"
            )
        else:
            requirements += f'**Requirements**: {course["prerequisites"]}\n'

        if course["corequisites"] != None:
            requirements += f'**Corequisites**: {course["corequisites"]}\n'

        if course["exclusions"] != None:
            requirements += f'**Exclusions**: {course["exclusions"]}\n'

        if course["recommended_preparation"] != None:
            requirements += (
                f"**Recommended Preparation**: {course['recommended_preparation']}\n"
            )

        cursor.execute(
            "INSERT INTO courses(school, code, number, department, name, description, requirements, units, campus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                "uoft",
                course_info[0],
                int(course_info[1]),
                course_info[2],
                course["name"],
                course["description"],
                requirements,
                academic_units,
                campus,
            ),
        )
