import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from courses.pull_courses import pull_course
from discord_slash.utils.manage_commands import create_option


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
            )
        ],
    )
    async def _course(self, ctx, course):
        if " " in course:
            course = course.split(" ")
            course = f"{course[0].upper()}-{course[1]}"
        else:
            final = ""
            dash = False
            for i in course:
                if i.isnumeric() and not dash:
                    final += "-" + i
                    dash = True
                else:
                    final += i

        result = await pull_course(final, "queens")

        if result[0] == True:
            await ctx.send(embed=result[1])
        else:
            await ctx.send(result[1], hidden=True)


def setup(bot):
    bot.add_cog(Slash_Help(bot))