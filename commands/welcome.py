import discord
from methods.database import database_connection
from methods.embed import create_embed, add_field


async def welcome_handling(ctx, client):
    """Handles welcoming new users."""
    db = await database_connection(ctx.guild.id)

    # Grabs this server's info
    welcome_info = db["db"].execute("SELECT * FROM welcome").fetchone()

    # Returns if there isn't any
    if welcome_info[2] == 0:
        return

    if welcome_info[0] == None or welcome_info[1] == None:
        return

    message = welcome_info[1]
    channel = welcome_info[0]

    # Send the message
    channel = client.get_channel(int(channel))
    await channel.send(message.replace("{{USER}}", ctx.mention))


async def welcome_setup(ctx, client, channel: int, description: str):
    """Sets up the welcome messages."""
    if ctx.author.guild_permissions.administrator != True:
        return

    db = await database_connection(ctx.guild.id)

    # Updates the DB
    db["db"].execute(
        "UPDATE welcome SET channel = ?, message = ?, enabled = ?",
        (channel, description, True),
    )
    db["con"].commit()

    # Send status message
    embed = create_embed("Welcome Message Created Successfully", "", "light_green")
    add_field(embed, "Message", description, True)
    add_field(embed, "Channel", channel, True)
    await ctx.channel.send(embed=embed, hidden=True)


async def welcome_toggle(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return

    db = await database_connection(ctx.guild.id)

    welcome_info = list(db["db"].execute("SELECT * FROM WELCOME").fetchone())
    if welcome_info[2] == 0:
        welcome_info[2] = 1
        embed = create_embed("Welcome Message Enabled", "", "light_green")
    else:
        welcome_info[2] = 0
        embed = create_embed("Welcome Message Disabled", "", "red")

    db["db"].execute(
        "UPDATE welcome SET channel = ?, message = ?, enabled = ?",
        (welcome_info[0], welcome_info[1], welcome_info[2]),
    )
    db["con"].commit()

    await ctx.channel.send(embed=embed, hidden=True)
