import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands.course import course as call_course
from discord_slash.utils.manage_commands import create_option, create_choice


class Slash_Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="course",
        description="Displays information about a course.",
        options=[
            create_option(
                name="course",
                description="The course code.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="school",
                description="The school the course is at.",
                option_type=3,
                required=False,
                choices=[
                    create_choice(name="Queens University", value="queens"),
                    create_choice(name="University of Waterloo", value="waterloo"),
                    create_choice(name='University of Toronto', value='uoft')
                ],
            ),
        ],
    )
    async def _course(self, ctx, course, school=None):
        if " " in course:
            course = course.split(" ")
            course = f"{course[0].upper()}-{course[1]}"
        else:
            final = ""
            dash = False
            for i in course:
                if i.isnumeric() and not dash:
                    final += "-" + i.upper()
                    dash = True
                else:
                    final += i.upper()

            course = final

        await call_course(ctx, course, school)


def setup(bot):
    bot.add_cog(Slash_Help(bot))