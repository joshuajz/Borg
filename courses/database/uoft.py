import json
import requests
import re
from methods.database import Courses_DB

base = "https://nikel.ml/api/courses"


async def get_info(offset=0):
    parameters = {"limit": 100, "offset": offset}

    response = requests.get(base, params=parameters)

    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))["response"]
    else:
        return False


async def pull_values():
    db = await Courses_DB("uoft")

    offset = 0
    while True:
        info = await get_info(offset)
        if info != False and len(info) != 0:
            await place_info(info, db)
            offset += 100
        else:
            break

    print("Finished UofT Courses.")


async def place_info(courses: list, db):
    """
    H1 - UTSG half year
    Y1 - UTSG full year

    H3 - UTSC half year
    Y3 - UTSC full year

    H5 - UTM half year
    Y5 - UTM full year
    """

    def split_code(code):
        r = re.compile("([a-zA-Z]+)([0-9]+)")
        m = r.match(code)
        return (code, m.group(1), m.group(2), code[-2::])

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

    in_database = await db.fetch_courses()

    for course in courses:
        code = course["code"]
        if code is None:
            break
        try:
            academic_units, campus = get_campus(code)
        except:
            break

        code = course_info = split_code(course["code"])
        code = code[1] + "-" + code[2] + code[3]

        if code in in_database:
            continue

        requirements = ""
        if course["prerequisites"] is None:
            requirements += "None (Check the UofT website to be sure.)\n"
        else:
            requirements += f'**Requirements**: {course["prerequisites"]}\n'

        if course["corequisites"] is not None:
            requirements += f'**Co-requisites**: {course["corequisites"]}\n'

        if course["exclusions"] is not None:
            requirements += f'**Exclusions**: {course["exclusions"]}\n'

        if course["recommended_preparation"] is not None:
            requirements += (
                f"**Recommended Preparation**: {course['recommended_preparation']}\n"
            )

        await db.add_course(
            code,
            int(course_info[2]),
            course_info[1],
            course["name"],
            course["description"],
            requirements=requirements,
            units=academic_units,
            campus=campus,
        )
