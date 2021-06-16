from courses.database.queens import pull_values as p_queens
from courses.database.uoft import pull_values as p_uoft
from courses.database.waterloo import pull_values as p_uw


async def pull_courses(bot):

    print("Pulling Queens Courses.")
    bot.loop.create_task(p_queens())

    print("Pulling UofT Courses")
    bot.loop.create_task(p_uoft())

    print("Pulling Waterloo Courses.")
    bot.loop.create_task(p_uw())
