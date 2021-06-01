import os
from dotenv import load_dotenv
from methods.database import create_database, database_connection

load_dotenv()


def setup_database():
    port = os.environ.get("database_port")
    if port:
        create_database(os.environ.get("database_password"), port=port)
    else:
        create_database(os.environ.get("database_password"))


setup_database()

port = os.environ.get("database_port")
if port:
    DATABASE_CONNECTION, DATABASE_CURSOR = database_connection(
        os.environ.get("database_password"), port=port
    )
else:
    DATABASE_CONNECTION, DATABASE_CURSOR = database_connection(
        os.environ.get("database_password")
    )
