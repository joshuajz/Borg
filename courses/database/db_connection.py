import os
from dotenv import load_dotenv
import sys


sys.path.append("../..")
from methods.database import create_database


def course_database_connection():
    os.chdir("../..")
    load_dotenv(f"{os.getcwd()}/.env")
    PASSWORD, PORT = os.environ.get("database_password"), os.environ.get(
        "database_port"
    )

    if PORT is None:
        return create_database(PASSWORD)
    else:
        return create_database(PASSWORD, port=PORT)
