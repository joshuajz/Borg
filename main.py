import discord
import os
import traceback
from methods.database import check_filesystem, database_connection
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from commands.commands import custom_command_handling
from commands.programs import programs_reaction_handling

load_dotenv()

# Intents
intents = discord.Intents().default()
intents.members = True
intents.reactions = True


slash_cogs = ("s_commands", "s_programs", "s_roles")
classic_cogs = ("c_commands", "c_programs")

# Bot Instance
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")

    await check_filesystem(bot)


@bot.listen()
async def on_message(ctx):
    print(ctx.content)

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
        print(command)
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


@bot.event
async def on_guild_join(guild):
    print("Temp")
    #! Create Filesystem Function in database.db
    await create_filesystem(bot)


for cog in slash_cogs:
    bot.load_extension(f"commands.slash_commands.{cog}")

for cog in classic_cogs:
    bot.load_extension(f"commands.classic_commands.{cog}")

# Runs the bot with the token in .env
bot.run(os.environ.get("bot_token"))