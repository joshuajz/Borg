import discord
import sqlite3
from methods.embed import create_embed, add_field
import json
import os


async def pull_course(course_code: str, school: str):

    db = {
        "con": sqlite3.connect(
            f"{os.path.dirname(os.path.dirname(__file__))}/courses/database/database.db"
        )
    }
    db["db"] = db["con"].cursor()

    if school == "queens":
        course = (
            db["db"]
            .execute("SELECT * FROM queens WHERE id = (?)", (course_code,))
            .fetchall()
        )

        if len(course) == 0:
            # No course w/ that specific code
            all_courses = (
                db["db"]
                .execute(
                    "SELECT id FROM queens WHERE department = (?)",
                    (course_code.split("-")[0],),
                )
                .fetchall()
            )

            course_list = ", ".join(all_courses) + "."

            return [
                False,
                "That is no a valid course.  Here is a list of all courses in that department: "
                + course_list,
            ]
        else:
            course = course[0]

            images = pull_json()
            embed = create_embed(f"**{course[0]}**", f"{course[4]}", "cyan")
            embed.set_thumbnail(url=images["queens"])

            requirements = course[5]
            if requirements is None or requirements == "":
                requirements = "Unknown/No requirements.  Check the Queens website for more information."

            add_field(embed, "Requirements", requirements.replace(". ", ".\n"), False)
            add_field(embed, "Academic Level", course[6], True)
            add_field(embed, "Units", course[7], True)

            return [True, embed]


def pull_json():
    with open(
        f"{os.path.dirname(os.path.dirname(__file__))}/courses/icons/uploaded_icons.json"
    ) as f:
        data = json.load(f)

    return data