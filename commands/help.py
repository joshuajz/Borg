import discord
from methods.embed import create_embed, add_field


async def help(ctx):
    """Help command"""
    pages = {}

    embed = create_embed("Help", "", "orange")
    add_field("!help or /help", "Provides this help command.", True)
    add_field(
        "/command",
        "Allows you to use this server's custom commands.\n/command add\n/command remove\n/command use",
        True,
    )
    add_field(
        "!commands or /command list",
        "Allows you to list out this server's commands.",
        True,
    )
    add_field(
        "/programs",
        "Allows you to manage your programs.\n/programs add\n/programs setup",
        True,
    )
    add_field("!programs or /programs programs", "Lists a user's programs", True)

    await ctx.send(embed=embed)