import sqlite3
import os
import sys
import asyncio

sys.path.append("../")
from methods.database import database_connection

ROOT_DIR = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}"
SERVERS_DIR = f"{ROOT_DIR}/Borg/servers"


async def main():
    commands = ["ALTER TABLE settings ADD courses_default_school text"]

    os.chdir(SERVERS_DIR)
    list_dir = os.listdir()
    for f in list_dir:

        db = await database_connection(f)

        for command in commands:
            db["db"].execute(command)
            db["con"].commit()


asyncio.run(main())