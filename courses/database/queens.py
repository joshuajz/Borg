import json
import requests
import sqlite3

base = "https://api.qmulus.io/v1/courses/"
db = sqlite3.connect("database.db")
cursor = db.cursor()


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


def create_database():
    cursor.execute(
        """CREATE TABLE "queens" (
	"id"	INTEGER NOT NULL,
    "course_code"	TEXT NOT NULL,
	"department"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"requirements"	TEXT NOT NULL,
	"academic_level"	TEXT NOT NULL,
	"units"	INTEGER NOT NULL
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


def place_info(items: list):
    for item in items:
        course_id = item["id"]
        course_code = item["course_code"]

        if item["units"] == 0:
            continue

        if course_id[-1] == "B" or course_id[-1] == "A":
            course_id = course_id[0:-1]

        if course_code[-1] == "B" or course_code[-1] == "A":
            course_code = course_code[0:-1]

        cursor.execute(
            "INSERT INTO queens VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                course_id,
                course_code,
                item["department"],
                item["course_name"],
                item["description"],
                item["requirements"],
                item["academic_level"],
                item["units"],
            ),
        )
    db.commit()


try:
    create_database()
except:
    print("Database already created.")

pull_values()