from methods.embed import create_embed, add_field, create_embed_template
import json
import os
import re
from methods.database import (
    database_connection,
    course_fetch_split,
    course_fetch,
    course_department_exist,
    course_codes_department,
    course_fetch_all,
    course_department_with_school,
)
from methods.paged_command import page_command

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE_IMAGES = json.load(open(f"{ROOT_DIR}/courses/icons/uploaded_icons.json", "r"))
SCHOOLS = ("queens", "waterloo", "uoft")


async def course_embed(course):
    settings = {
        "queens": (True, True, True, False),
        "waterloo": (True, False, False, False),
        "uoft": (True, False, True, True),
    }
    requirements, academic_level, units, campus = settings[course["school"]]

    embed = create_embed(
        f"{course['code']} - {course['name']}",
        course["description"],
        "cyan",
        thumbnail=COURSE_IMAGES[course["school"]],
    )

    if requirements and course["school"] == "queens":
        requirements = (
            course["requirements"].replace(". ", ".\n")
            if course["requirements"]
            else None
        )
    elif course["requirements"] is None:
        requirements = "Unknown/No Requirements.  Check the website."
    else:
        requirements = course["requirements"]

    if requirements:
        add_field(embed, "Requirements", requirements, False)

    if academic_level:
        add_field(embed, "Academic Level", course["academic_level"], True)

    if units:
        add_field(embed, "Units", course["units"], True)

    if campus:
        add_field(embed, "Campus", course["campus"], True)

    return embed


async def course(ctx, bot, course_name: str, school=None):
    def split_code(code):
        m = re.compile("([a-zA-z]+)([0-9]+)?([H|Y][1|3|5])?")
        m = m.match(code)
        return {
            "code": m.group(0),
            "department": m.group(1),
            "number": int(m.group(2)),
            "uoft": m.group(3),
        }

    db = await database_connection()
    course_split = split_code(course_name)

    if school:
        if course_split["uoft"]:
            course_fetched = await course_fetch_split(
                course_split["department"], course_split["number"], db
            )
        else:
            course_fetched = await course_fetch(school, course_name, db)

        if len(course_fetched) == 0:
            department = course_split["department"]
            department_fetch = await course_department_exist(school, department, db)

            if department_fetch:
                codes = await course_codes_department(school, department, db)

                multiple_courses = [f"**{i['code']}** - *{i['name']}*" for i in codes]
                multiple_courses.sort()

                await page_command(
                    ctx,
                    bot,
                    multiple_courses,
                    f"{school.capitalize()} Courses w/ the {department} department.",
                )

                return True, None
        elif len(course_fetched) == 1:
            embed = await course_embed(course_fetched[0])
            return True, embed
    else:
        if course_split["uoft"]:
            fetched_course = await course_fetch_split(
                course_split["department"], course_split["number"], db
            )
            if fetched_course:
                return True, await course_embed(fetched_course[0])

        options = await course_fetch_all(course_name, db)

        if len(options) == 1:
            return True, await course_embed(options[list(options.keys())[0]])
        elif len(options) == 0:
            schools_w_department = await course_department_with_school(
                course_split["department"], db
            )
        else:
            # Multiple courses provided.
            courses = [f"{i[0].capitalize()}: {i[1]}" for i in options]
            await page_command(ctx, bot, courses, "Possible Courses & Schools:")

        if len(schools_w_department) == 0:
            return False, await create_embed_template(
                "Invalid Department",
                "That department couldn't be found at any of the schools in my dataset.",
                "error",
            )
        if len(schools_w_department) == 1:
            school = [i[0] for i in schools_w_department]
            school = list(dict.fromkeys(school))

            courses = await course_codes_department(
                school[0], grab_faculty(course_name).upper(), db
            )

            courses = [f"**{i['code']}** - *{i['name']}*" for i in courses]

            await page_command(
                ctx,
                bot,
                courses,
                f"{courses[0].capitalize()} Courses with the {course_name.strip().upper()} department.",
            )
        else:
            return False, await create_embed_template(
                "Valid Department -> Multiple Schools",
                "You provided a valid department, but multiple schools share that same department name.  Please provide a department and school name.",
                "error",
            )


def grab_faculty(course):
    final = ""
    for char in course:
        if char.isalpha():
            final += char
    return final
