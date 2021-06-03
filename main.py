import discord
import os
import traceback
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from methods.database import create_database
from commands.commands import custom_command_handling
from commands.programs import programs_reaction_handling
from commands.welcome import welcome_handling

load_dotenv()

# Intents
intents = discord.Intents().default()
intents.members = True
intents.reactions = True

# Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

slash_cogs = ("s_commands", "s_programs", "s_roles", "s_help", "s_course")
classic_cogs = ("c_commands", "c_programs", "c_roles", "c_help")

# Bot Instance
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Remove the default bot command
bot.remove_command("help")


@bot.event
async def on_ready():
    port = os.environ.get("database_port")
    if port:
        create_database(os.environ.get("database_password"), port=port)
    else:
        create_database(os.environ.get("database_password"))

    print(f"Logged in as {bot.user}.")


@bot.listen()
async def on_message(ctx):
    if ctx.content != None and ctx.author != None:
        print(f"{ctx.guild.name} - {ctx.author.name}: {ctx.content}")

    # Don't do anything with a bot's message
    if ctx.author == bot.user:
        return

    # Potential regex: (?<=^!)(\w*)

    if ctx.content.startswith("!"):
        if "\n" in ctx.content:
            command = (
                ctx.content.split("\n")[0]
                .split(" ")[0]
                .strip()
                .replace("!", "")
                .lower()
            )
        else:
            command = ctx.content[1::].split(" ")[0].lower().strip().lower()

        await custom_command_handling(ctx, command)


@bot.event
async def on_raw_reaction_add(ctx):
    if ctx.member.bot:
        return

    if await programs_reaction_handling(ctx, bot) == True:
        return


@bot.event
async def on_member_join(ctx):
    await welcome_handling(ctx, bot)


for cog in slash_cogs:
    bot.load_extension(f"commands.slash_commands.{cog}")

for cog in classic_cogs:
    bot.load_extension(f"commands.classic_commands.{cog}")

# Runs the bot with the token in .env
bot.run(os.environ.get("bot_token"))