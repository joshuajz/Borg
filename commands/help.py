import discord.ext
from methods.embed import create_embed, add_field
from methods.paged_command import send_page_command


async def help_command(ctx: discord.ext.commands.Context, bot: discord.ClientUser.bot):
    """Help Command

    Args:
        ctx (discord.ext.commands.Context): Context
        bot (discord.ClientUser.bot): Bot instance
    """

    def check(reaction, user):
        """Checks if the original reaction was added by the user provided."""
        return user == ctx.author and str(reaction) in ["◀️", "▶️"]

    pages = []

    embed = create_embed(
        "Help: Table of Contents",
        "Page `1/4`\nPage 1: Table of Contents\nPage 2: General Commands\nPage 3: University Commands\nPage 4: Setup Commands",
        "orange",
    )
    pages.append(embed)

    embed = create_embed("Help: General Commands", "Page `2/4`", "orange")
    add_field(
        embed,
        "Commands",
        "Allow you to use this server's custom commands.\n!commands - Lists the commands.",
        False,
    )
    pages.append(embed)

    embed = create_embed("Help: University Commands", "Page `3/4`", "orange")
    add_field(
        embed,
        "Programs",
        "Allows you to interact with programs lists.\n!programs - Allows you to see a user's programs.\n/programs add - Add programs.\n/programs remove - Remove programs.\n/programs edit - Edit one of your programs.\n",
        False,
    )
    add_field(
        embed,
        "Courses",
        "Allows you to lookup a University's course.\n/course - Lookup a course.",
        False,
    )
    pages.append(embed)

    embed = create_embed("Help: Setup Commands", "Page `4/4`", "orange")
    add_field(
        embed,
        "Programs",
        "Allows you to setup the channel for programs verification.\n/programs setup {channel}\n",
        False,
    )
    add_field(
        embed,
        "Commands",
        "Allows you to add and remove your server's custom commands.\n/command add - Adds a command.\n/command remove - Removes a command.",
        False,
    )
    pages.append(embed)

    # Send the original message w/ reactions
    await send_page_command(ctx, bot, pages)
