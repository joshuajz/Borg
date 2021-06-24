import json
import requests
from methods.database import Courses_DB


base = "https://api.qmulus.io/v1/courses/"


async def get_info(offset=0):
    parameters = {
        "limit": "100",
        "offset": str(offset),
    }

    response = requests.get(base, params=parameters)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return False


async def pull_values():
    db = await Courses_DB("queens")

    courses = await db.fetch_courses()

    offset = 0
    while True:
        info = await get_info(offset)
        if info != False and len(info) != 0:
            await place_info(info, courses, db)
            offset += 100
        else:
            break

    print("Finished Queens Courses.")


async def place_info(items: list, in_database, db):
    for item in items:
        course_id = item["id"].replace("-", "")
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

        if course_id in in_database:
            continue

        await db.add_course(
            course_id,
            int(course_code),
            item["department"],
            item["course_name"],
            item["description"],
            requirements=requirements,
            academic_level=item["academic_level"],
            units=item["units"],
        )
