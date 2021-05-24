import discord
import sqlite3
from methods.embed import create_embed, add_field
import json
import os

# Options:
# User provides course and school -> return the course if it exists, otherwise return a list of courses in that faculty
# User provides course and school is auto picked from discord -> return the course if it exists, otherwise return a list of courses in that faculty
# User provides a course code and no school and no school default -> find that course code at various unis and release it, otherwise return nothing

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE_IMAGES = json.load(open(f"{ROOT_DIR}/courses/icons/uploaded_icons.json", "r"))
SCHOOLS = ("queens", "waterloo")


async def queens_embed(course):
    embed = create_embed(
        f"{course[0]} - {course[3]}",
        course[4],
        "cyan",
        thumbnail=COURSE_IMAGES["queens"],
    )

    requirements = course[5]
    if requirements is None or requirements == "":
        requirements = (
            "Unknown/No requirements.  Check the Queens website for more information."
        )

    add_field(embed, "Requirements", requirements.replace(". ", ".\n"), False)
    add_field(embed, "Academic Level", course[6], True)
    add_field(embed, "Units", course[7], True)

    return embed


async def waterloo_embed(course):
    embed = create_embed(
        f"{course[0]} - {course[3]}",
        course[4],
        "cyan",
        thumbnail=COURSE_IMAGES["waterloo"],
    )

    requirements = course[5]
    if requirements is None or requirements == "":
        requirements = (
            "Unknown/No Requirements.  Check the Waterloo website for more information."
        )

    add_field(embed, "Requirements", requirements, False)

    return embed


SCHOOL_EMBEDS = {"queens": queens_embed, "waterloo": waterloo_embed}


async def course(ctx, course, school):
    db = course_database()

    if school:
        course_fetched = (
            db["db"]
            .execute("SELECT * FROM (?) WHERE id = (?)", (school, course))
            .fetchall()
        )

        # Found the course
        if len(course_fetched) == 1:
            embed = await SCHOOL_EMBEDS[school](course_fetched[0])
            await ctx.send(embed=embed)
        elif len(course_fetched) == 0:
            faculty = grab_faculty(course)

            # Check to see if a proper faculty was provided
            if (
                db["db"].execute(
                    "SELECT COUNT(department) FROM (?) WHERE department = (?)",
                    (school, faculty),
                )
            ) > 0:

                multiple_courses = (
                    db["db"]
                    .execute(
                        "SELECT id FROM (?) WHERE department = (?)", (school, faculty)
                    )
                    .fetchall()
                )

                embed = create_embed(
                    "Invalid Course Code.",
                    f'The code you provided was invalid.  Here are some courses from the same school and department: {", ".join(multiple_courses)}',
                    "cyan",
                )
                await ctx.send(embed=embed, hidden=True)
            else:
                embed = create_embed(
                    "Invalid Course Code",
                    "The course code you provided was invalid, and I couldn't find any courses in that department.",
                    "cyan",
                )
                await ctx.send(embed=embed, hidden=True)
    else:
        # We don't have a school so we're going to need to query every school that we have for that course code
        results = grab_courses(course)

        if len(results) == 0:
            await ctx.send(
                "Invalid Course Code.  I could not find that course at any of the schools in my database.",
                hiddne=True,
            )
        elif len(results) == 1:
            for school, course in results.items():
                embed = await SCHOOL_EMBEDS[school](course)
                await ctx.send(embed=embed)
        else:
            # Multiple courses provided.
            await ctx.send(
                "Multiple schools have that course, please provide a school.",
                hidden=True,
            )


def grab_courses(course):
    db = course_database()

    results = {}

    for school in SCHOOLS:

        result = (
            db["db"]
            .execute(f"SELECT * FROM {school} WHERE id = (?)", (course,))
            .fetchone()
        )
        if result:
            results[school] = result

    return results


def grab_faculty(course):
    final = ""
    for l in course:
        if l.isalpha():
            final += l
    return final


def course_database():
    con = sqlite3.connect(f"{ROOT_DIR}/courses/database/database.db")
    return {"db": con.cursor(), "con": con}
