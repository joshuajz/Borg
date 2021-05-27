import json
import requests
import sqlite3
import re

base = "https://nikel.ml/api/courses"
db = sqlite3.connect("database.db")
cursor = db.cursor()


def get_info(offset=0):
    parameters = {"limit": 100, "offset": offset}

    response = requests.get(base, params=parameters)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))["response"]
    else:
        return False


def create_database():
    cursor.execute(
        """CREATE TABLE "uoft" (
        "id" TEXT NOT NULL,
        "course_code" INTEGER NOT NULL,
        "department" TEXT NOT NULL,
        "name" TEXT NOT NULL,
        "description" TEXT,
        "requirements" TEXT 
    );"""
    )
    db.commit()


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

    """
    H1 - UTSG half year
    Y1 - UTSG full year

    H3 - UTSC half year
    Y3 - UTSC full year

    H5 - UTM half year
    Y5 - UTM full year
    """

    current_courses = [
        i[0] for i in cursor.execute("SELECT course_code FROM waterloo").fetchall()
    ]

    for course in courses:
        print(course)
        break
        code = course["code"]

        course_info = split_code(code)

        if course_info[0] in current_courses:
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
            "INSERT INTO uoft VALUES (?, ?, ?, ?, ?, ?)",
            (
                course_info[0],
                int(course_info[1]),
                course_info[2],
                course["name"],
                course["description"],
                requirements,
            ),
        )
        db.commit()


try:
    create_database()
except:
    print("Database already created.")

pull_values()
