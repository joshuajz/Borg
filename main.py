import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from methods.database import create_database, Guild_DB
from commands.commands import custom_command_handling
from commands.programs import programs_reaction_handling
from commands.welcome import welcome_handling
from courses.database.pull_courses import pull_courses

load_dotenv()

# Intents
intents = discord.Intents().default()
intents.members = True
intents.reactions = True

# Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# List of slash commands and classic commands
slash_cogs = ("s_commands", "s_programs", "s_roles", "s_help", "s_course")
classic_cogs = ("c_commands", "c_programs", "c_roles", "c_help")

# Bot Instance
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Remove the default bot command
bot.remove_command("help")


@bot.event
async def on_ready():
    """When the bot starts up."""

    await create_database()

    await pull_courses(bot)

    # Default Settings Check
    guilds_on = [guild.id for guild in bot.guilds]
    database = await Guild_DB(0)
    guilds_db = await database.db.fetch("SELECT guild_id FROM settings")
    guilds_db = [i[0] for i in guilds_db]
    if guilds_db is not None:
        for guild in guilds_on:
            if guild not in guilds_db:
                await (await Guild_DB(guild)).create_default_settings()

    print(f"Logged in as {bot.user}.")


@bot.listen()
async def on_message(message: discord.Message):
    """When a message is sent."""

    if (
        message
        and message.content != None
        and message.author != None
        and message.author.name != None
    ):
        print(f"{message.guild.name} - {message.author.name}: {message.content}")

    # Don't do anything with a bot's message
    if message.author == bot.user:
        return

    # Potential regex: (?<=^!)(\w*)

    if message.content.startswith("!"):
        if "\n" in message.content:
            command = (
                message.content.split("\n")[0]
                .split(" ")[0]
                .strip()
                .replace("!", "")
                .lower()
            )
        else:
            command = message.content[1::].split(" ")[0].lower().strip().lower()

        await custom_command_handling(message, command)


@bot.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
    """When a reaction is added."""

    if reaction.member.bot:
        return

    if await programs_reaction_handling(reaction, bot) == True:
        return


@bot.event
async def on_member_join(member: discord.Member):
    """When a member joins the server."""

    await welcome_handling(member, bot)


@bot.event
async def on_guild_join(guild: discord.Guild):
    """When the bot joins a guild."""

    await (await Guild_DB(guild.guild.id)).create_default_settings()


# Load the various commands
for cog in slash_cogs:
    bot.load_extension(f"commands.slash_commands.{cog}")

for cog in classic_cogs:
    bot.load_extension(f"commands.classic_commands.{cog}")

# Runs the bot with the token in .env
bot.run(os.environ.get("bot_token"))
