import discord
import sqlite3
from methods.embed import create_embed, add_field
import json
import os
from methods.database import database_connection
from methods.paged_command import page_command

# Options:
# User provides course and school -> return the course if it exists, otherwise return a list of courses in that faculty
# User provides course and school is auto picked from discord -> return the course if it exists, otherwise return a list of courses in that faculty
# User provides a course code and no school and no school default -> find that course code at various unis and release it, otherwise return nothing

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE_IMAGES = json.load(open(f"{ROOT_DIR}/courses/icons/uploaded_icons.json", "r"))
SCHOOLS = ("queens", "waterloo", "uoft")


async def course_embed(course):
    if course[0] == "queens":
        requirements, academic_level, units = True, True, True
    elif course[0] == "waterloo":
        requirements, academic_level, units = True, False, False
    # elif course[0] == 'uoft':

    embed = create_embed(
        f"{course[1]} - {course[4]}",
        course[5],
        "cyan",
        thumbnail=COURSE_IMAGES[course[0]],
    )

    if requirements:
        if course[0] == "queens":
            requirements = course[6]
            if requirements is None or requirements == "":
                requirements = "Unknown/No Requirements.  Check the website."
            else:
                requirements = requirements.replace(". ", ".\n")
        elif course[0] in ["waterloo"]:
            requirements = course[6]
            if requirements is None:
                requirements = "Unknown/No Requirements.  Check the university website."
        else:
            requirements = course[6]

        add_field(embed, "Requirements", requirements, False)

    if academic_level:
        add_field(embed, "Academic Level", course[7], True)

    if units:
        add_field(embed, "Units", course[8], True)


async def course(ctx, bot, course, school=None):
    db, cursor = database_connection()

    if school:
        cursor.execute(
            "SELECT * FROM courses WHERE school = %s AND code = %s", (school, course)
        )
        course_fetched = cursor.fetchall()

        if course_fetched is None or len(course_fetched) == 0:
            faculty = grab_faculty(course)

            cursor.execute(
                "SELECT COUNT(department) FROM courses WHERE school = %s AND department = %s",
                (school, faculty),
            )

            # Check to see if a proper faculty was provided
            if cursor.fetchone() is None:
                cursor.execute(
                    "SELECT code FROM courses WHERE school = %s AND department = %s",
                    (school, faculty.strip().upper()),
                )
                multiple_courses = cursor.fetchall()
                multiple_courses = [f"**{i[1]}** - *{i[4]}*" for i in multiple_courses]
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
        results = grab_courses(course)

        if len(results) == 0:
            print(course.strip())
            cursor.execute(
                "SELECT school FROM courses WHERE department = %s",
                (course.strip().upper(),),
            )
            results = cursor.fetchall()
            if results is not None:
                results = [i[0] for i in results]
                results = list(dict.fromkeys(results))

                if len(results) == 1:
                    cursor.execute(
                        "SELECT * FROM courses WHERE school = %s AND department = %s",
                        (results[0], course.strip().upper()),
                    )

                    courses = cursor.fetchall()
                    courses = [f"**{i[1]}** - *{i[4]}*" for i in courses]
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
            for school, course in results.items():
                embed = await course_embed(course)
                await ctx.send(embed=embed)
        else:
            # Multiple courses provided.
            courses = [f"{i[0].capitalize()}: {i[1]}" for i in results]
            await page_command(ctx, bot, courses, "Possible Courses & Schools:")


def grab_courses(course):
    db, cursor = database_connection()

    results = {}

    for school in SCHOOLS:
        cursor.execute(
            "SELECT * FROM courses WHERE school = %s AND code = %s", (school, course)
        )
        result = cursor.fetchone()

        if result:
            results[school] = result

    return results


def grab_faculty(course):
    final = ""
    for l in course:
        if l.isalpha():
            final += l
    return final
