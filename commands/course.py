import discord
from methods.embed import create_embed, add_field
import json
import os
from methods.database import Courses_DB
from methods.paged_command import page_command

# Options:
# User provides course and school -> return the course if it exists, otherwise return a list of courses in that faculty
# User provides course and school is auto picked from discord -> return the course if it exists, otherwise return a list of courses in that faculty
# User provides a course code and no school and no school default -> find that course code at various unis and release it, otherwise return nothing

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE_IMAGES = json.load(open(f"{ROOT_DIR}/courses/icons/uploaded_icons.json", "r"))
SCHOOLS = ("queens", "waterloo", "uoft")


async def course_embed(course):
    if course["school"] == "queens":
        requirements, academic_level, units = True, True, True
    elif course["school"] == "waterloo":
        requirements, academic_level, units = True, False, False
    # elif course[0] == 'uoft':

    embed = create_embed(
        f"{course['code']} - {course['name']}",
        course["description"],
        "cyan",
        thumbnail=COURSE_IMAGES[course["school"]],
    )

    if requirements:
        if course["school"] == "queens":
            requirements = course["requirements"]
            if requirements is None or requirements == "":
                requirements = "Unknown/No Requirements.  Check the website."
            else:
                requirements = requirements.replace(". ", ".\n")
        elif course["school"] == "waterloo":
            requirements = course["requirements"]
            if requirements is None:
                requirements = "Unknown/No Requirements.  Check the university website."
        else:
            requirements = course[6]

        add_field(embed, "Requirements", requirements, False)

    if academic_level:
        add_field(embed, "Academic Level", course[7], True)

    if units:
        add_field(embed, "Units", course[8], True)

    return embed


async def course(ctx, bot, course, school=None):
    db = await Courses_DB(school)

    if school:
        course_fetched = await db.fetch_course(course)

        if len(course_fetched) == 0:
            faculty = grab_faculty(course)

            department_fetch = await db.department_exist(faculty)

            # Check to see if a proper faculty was provided
            if department_fetch:
                codes = await db.fetch_codes_from_department(faculty)

                multiple_courses = [f"**{i['code']}** - *{i['name']}*" for i in codes]
                multiple_courses.sort()

                await page_command(
                    ctx,
                    bot,
                    multiple_courses,
                    f"{school.capitalize()} Courses w/ the {faculty} department.",
                )
            else:
                embed = create_embed(
                    "Invalid Course Code",
                    "The course code you provided was invalid, and I couldn't find any courses in that department.",
                    "cyan",
                )
                await ctx.send(embed=embed, hidden=True)
        elif len(course_fetched) == 1:
            embed = await course_embed(course_fetched[0])
            await ctx.send(embed=embed)

    else:
        # We don't have a school so we're going to need to query every school that we have for that course code
        results = await db.fetch_courses_all(course=course)

        if len(results) == 0:

            results = await db.fetch_schools_with_department(course.strip().upper())
            if results is not None:
                results = [i[0] for i in results]
                results = list(dict.fromkeys(results))

                if len(results) == 1:
                    db.school = results[0]
                    courses = await db.fetch_codes_from_department(
                        grab_faculty(course).upper()
                    )

                    courses = [f"**{i['code']}** - *{i['name']}*" for i in courses]
                    await page_command(
                        ctx,
                        bot,
                        courses,
                        f"{results[0].capitalize()} Courses w/ the {course.strip().upper()} department.",
                    )
                    return
            else:
                await ctx.send(
                    "You provided a valid department, but multiple schools share that same department name.  Please provide a department and school name.",
                    hidden=True,
                )
        elif len(results) == 1:
            embed = await course_embed(course[0])
            await ctx.send(embed=embed)
        else:
            # Multiple courses provided.
            courses = [f"{i[0].capitalize()}: {i[1]}" for i in results]
            await page_command(ctx, bot, courses, "Possible Courses & Schools:")


def grab_faculty(course):
    final = ""
    for l in course:
        if l.isalpha():
            final += l
    return final
