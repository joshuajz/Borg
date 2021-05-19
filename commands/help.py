import discord
from methods.embed import create_embed, add_field


async def help_command(ctx):
    """Help command"""
    pages = {}

    embed = create_embed("Help", "", "orange")
    add_field(embed, "!help or /help", "Provides this help command.", True)
    add_field(
        embed,
        "/command",
        "Allows you to use/edit this server's custom commands.\n/command add\n/command remove\n/command use",
        True,
    )
    add_field(
        embed,
        "!commands or /command list",
        "Allows you to list out this server's commands.",
        True,
    )
    add_field(
        embed,
        "/programs",
        "Allows you to manage your programs.\n/programs add\n/programs setup\n/programs programs\n/programs edit\n/programs remove",
        True,
    )
    add_field(embed, "!programs or /programs programs", "Lists a user's programs", True)

    pages[1] = embed

    await ctx.send(embed=embed)