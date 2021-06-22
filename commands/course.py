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
    requirements, academic_level, units, campus = False, False, False, False
    print(course)
    if course["school"] == "queens":
        requirements, academic_level, units = True, True, True
    elif course["school"] == "waterloo":
        requirements = True
    elif course["school"] == "uoft":
        requirements, units, campus = True, True, True

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
            requirements = course["requirements"]

        add_field(embed, "Requirements", requirements, False)

    if academic_level:
        add_field(embed, "Academic Level", course["academic_level"], True)

    if units:
        add_field(embed, "Units", course["units"], True)

    if campus:
        add_field(embed, "Campus", course["campus"], True)

    return embed


async def course(ctx, bot, course_name: str, school=None):
    print(school)
    db = await Courses_DB(school)

    if school:
        course_fetched = await db.fetch_course(course_name)

        if len(course_fetched) == 0:
            faculty = grab_faculty(course_name)

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
        results = await db.fetch_courses_all(course=course_name)

        if len(results) == 0:

            results = await db.fetch_schools_with_department(
                course_name.strip().upper()
            )

            if len(results) >= 1:
                results = [i[0] for i in results]
                results = list(dict.fromkeys(results))

                if len(results) == 1:
                    db.school = results[0]
                    courses = await db.fetch_codes_from_department(
                        grab_faculty(course_name).upper()
                    )

                    courses = [f"**{i['code']}** - *{i['name']}*" for i in courses]

                    await page_command(
                        ctx,
                        bot,
                        courses,
                        f"{results[0].capitalize()} Courses w/ the {course_name.strip().upper()} department.",
                    )
                else:
                    await ctx.send(
                        "You provided a valid department, but multiple schools share that same department name.  Please provide a department and school name.",
                        hidden=True,
                    )
        elif len(results) == 1:
            embed = await course_embed(results[list(results.keys())[0]])
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
