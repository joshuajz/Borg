from discord.ext import commands
from discord_slash import cog_ext
from commands.course import course as call_course
from discord_slash.utils.manage_commands import create_option, create_choice


class SlashCourse(commands.Cog):
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
                    create_choice(name="University of Toronto", value="uoft"),
                ],
            ),
        ],
    )
    async def _course(self, ctx, course, school=None):
        """/course"""

        course = course.replace(" ", "")

        course = course.replace("-", "")

        result = await call_course(ctx, self.bot, course, school)
        if result[0] is True:
            await ctx.send(embed=result[1])
        elif result[0] is False and result[1] is not None:
            await ctx.send(embed=result[1], hidden=True)


def setup(bot):
    bot.add_cog(SlashCourse(bot))
