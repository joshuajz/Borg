from methods.database import create_database
from dotenv import load_dotenv
import os

# Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(f"{ROOT_DIR}/.env")


create_database(
    str(os.environ.get("database_password")),
    port=str(os.environ.get("database_port")),
)