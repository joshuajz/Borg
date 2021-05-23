import sqlite3
import os
import sys
import asyncio

sys.path.append("../")
from methods.database import database_connection
from methods.database import SERVERS_DIR


async def main():
    target_database = f"{SERVERS_DIR}/target.db"
    os.chdir(SERVERS_DIR)
    list_dir = os.listdir()
    for f in list_dir:

        db = await database_connection(f)

        tables = (
            db["db"]
            .execute("SELECT name FROM sqlite_master WHERE type='table'")
            .fetchall()
        )

        schema = {}

        for table in tables:
            schema[table[0]] = (
                db["db"].execute(f"PRAGMA table_info({table[0]})").fetchall()
            )
        print(schema)
        break


asyncio.run(main())