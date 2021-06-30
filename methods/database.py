import asyncpg
from dotenv import load_dotenv
import os


async def get_credentials():
    while ".env" not in os.listdir():
        try:
            os.chdir("..")
            if os.getcwd() == "/" or os.getcwd() == "\\":
                break

        except Exception as e:
            print(
                "Error moving directories.  Make sure you haven't renamed the folder that Borg resides in."
            )
            print(e)

    load_dotenv()
    port = os.environ.get("database_port")
    if port is None or port == "" or port == " ":
        port = None

    return os.environ.get("database_password"), port


async def create_database():
    """Create the default postgresql database."""

    password, port = await get_credentials()

    print("Creating Database.")

    # Connect to the default database
    try:
        con = await asyncpg.connect(
            database="postgres",
            user="postgres",
            password=password,
            host="localhost",
            port=port,
        )
    except OSError:
        print(
            "Unable to connect to database.  Did you start your postgresql database?  Stopping the program."
        )
        return False

    # Create the Borg database
    try:
        await con.execute("CREATE database borg")
    except Exception as e:
        print("Database Already Created.")
        print(e)

    # Connect to the borg database
    con = await database_connection()

    # Create the tables
    commands = [
        """CREATE TABLE custom_commands (
        guild_id bigint,
        command text,
        output text,
        image text
    )""",
        """CREATE TABLE command_roles (
        guild_id bigint,
        role_id bigint,
        command text
    )""",
        """CREATE TABLE programs (
        guild_id bigint,
        user_id bigint,
        description text
    )""",
        """CREATE TABLE settings (
        guild_id bigint,
        programs_channel bigint,
        courses_default_school varchar(255)
    )
    """,
        """CREATE TABLE welcome (
        guild_id bigint,
        channel bigint,
        message text,
        enabled boolean
    )""",
        """CREATE TABLE courses (
            school text,
            code varchar(25),
            number smallint,
            department varchar(200),
            name text,
            description text,
            requirements text,
            academic_level text,
            units decimal,
            campus text
    )""",
    ]

    for command in commands:
        async with con.transaction():
            try:
                await con.execute(command)
            except asyncpg.exceptions.DuplicateTableError as e:
                print(e)

    return con


async def database_connection():
    """Creates a connection to the Borg database."""

    password, port = await get_credentials()

    # Connect
    con = await asyncpg.connect(
        database="borg",
        user="postgres",
        password=password,
        host="localhost",
        port=int(port),
    )

    return con


async def program_grab(
    user_id: int, guild_id: int, db: asyncpg.Connection
) -> str or None:
    """Return's a user's programs.

    Args:
        user_id (int): User's ID
        guild_id (int): Guild's ID
        db (asyncpg.Connection): Database Connection

    Returns:
        str or None: Provides either the programs or None
    """

    programs_response = await db.fetchrow(
        "SELECT description FROM programs WHERE guild_id = $1 AND user_id = $2",
        guild_id,
        user_id,
    )

    if programs_response:
        return programs_response[0]
    else:
        return None


async def program_update(
    user_id: int, guild_id: int, new_programs: str, db: asyncpg.Connection
):
    """Update a user's programs.

    Args:
        user_id (int): User's ID
        guild_id (int): Guild's ID
        new_programs (str): New Programs
        db (asyncpg.Connection): Database Connection
    """

    await db.execute(
        "UPDATE programs SET description = $1 WHERE guild_id = $2 AND user_id = $3",
        new_programs,
        guild_id,
        user_id,
    )


async def program_check_exist(
    user_id: int, guild_id: int, db: asyncpg.Connection
) -> bool:
    """Checks to see if a user has a programs instance.

    Args:
        user_id (int): User's ID
        guild_id (int): Guild's ID
        db (asyncpg.Connection): Database Connection

    Returns:
        bool: Whether a programs instance exists for the user
    """

    result = await db.fetchrow(
        "SELECT COUNT(user_id) FROM programs WHERE guild_id = $1 AND user_id = $2",
        guild_id,
        user_id,
    )
    return False if result[0] == 0 else True


async def program_add(
    user_id: int, guild_id: int, programs: str, db: asyncpg.Connection
):
    """Add a programs instance.

    Args:
        user_id (int): User's ID
        guild_id (int): Guild's ID
        programs (str): Programs String
        db (asyncpg.Connection): Database Connection
    """

    await db.execute(
        "INSERT INTO programs VALUES ($1, $2, $3)", guild_id, user_id, programs
    )


async def program_delete(guild_id: int, user_id: int, db: asyncpg.Connection):
    """Removes a user's programs instance

    Args:
        guild_id (int): The Guild's ID
        user_id (int): The User's ID
        db (asyncpg.Connection): Database Connection
    """
    await db.execute(
        "DELETE FROM programs WHERE guild_id = $1 AND user_id = $2",
        guild_id,
        user_id,
    )


async def program_update(
    guild_id: int, user_id: int, message: str, db: asyncpg.Connection
):
    """Updates a user's programs instance

    Args:
        guild_id (int): The Guild's ID
        user_id (int): The User's ID
        message (int): The new message
        db (asyncpg.Connection): Database Connection
    """
    await db.execute(
        "UPDATE programs SET description = $1 WHERE guild_id = $2 AND user_id = $3",
        message,
        guild_id,
        user_id,
    )


async def role_grab(guild_id, db) -> list:
    """Provides all of the classic roles on a server.

    Args:
        guild_id (int): Guild's ID
        db (asyncpg.Connection): Database Connection

    Returns:
        list: Provides an empty list or a list of asyncpg.Record
            (
                role_id (int): Role's ID
                command (str): The command to toggle the role
            )
    """

    roles = await db.fetch(
        "SELECT role_id, command FROM command_roles WHERE guild_id = $1",
        guild_id,
    )

    return roles


async def role_find(
    guild_id: int, db: asyncpg.Connection, command=None, role_id=None
) -> asyncpg.Record:
    """Finds a role based off of a command or role_id

    Args:
        guild_id (int): Guild's ID
        db (asyncpg.Connection): Database Connection
        command (str): The command that toggles the role
        role_id (int): The role's ID

    Returns:
        None or asyncpg.Record: Provides None (no role) or a asyncpg.Record
            (
                guild_id (int): Guild's ID
                role_id (int): Role's ID
                command (str): The command that toggles the role
            )
    """

    if command:
        command_response = await db.fetchrow(
            "SELECT * FROM command_roles WHERE guild_id = $1 AND command = $2",
            guild_id,
            command,
        )

        return command_response

    elif role_id:

        command_response = await db.fetchrow(
            "SELECT * FROM command_roles WHERE guild_id = $1 AND role_id = $2",
            guild_id,
            role_id,
        )

        return command_response


async def role_check(
    guild_id: int, role_id: int, command: str, db: asyncpg.Connection
) -> bool:
    """Check to see if a role exists

    Args:
        guild_id (int): Guild's ID
        role_id (int): Role's ID
        command (str): The command that toggles the role
        db (asyncpg.Connection): Database Connection

    Returns:
        bool: Whether the role exists
    """

    role_response = await db.fetchrow(
        "SELECT EXISTS(SELECT * FROM command_roles WHERE guild_id = $1 AND (role_id = $2 OR command = $3))",
        guild_id,
        role_id,
        command,
    )

    return not (role_response["exists"])


async def role_add(guild_id: int, role_id: int, command: str, db: asyncpg.Connection):
    """Add a role to the database

    Args:
        guild_id (int): Guild's ID
        role_id (int): Role's ID
        command (str): The command that toggles the role
        db (asyncpg.Connection): Database Connection
    """

    async with db.transaction():
        try:
            await db.execute(
                "INSERT INTO command_roles VALUES ($1, $2, $3)",
                guild_id,
                role_id,
                command,
            )

        except Exception as e:
            print(e)


async def role_remove(guild_id: int, role_id: int, db: asyncpg.Connection):
    """Remove a role from the database

    Args:
        guild_id (int): Guild's ID
        role_id (int): Role's ID
        db (asyncpg.Connection): Database Connection
    """

    async with db.transaction():
        try:
            await db.execute(
                "DELETE FROM command_roles WHERE guild_id = $1 AND role_id = $2",
                guild_id,
                role_id,
            )
        except Exception as e:
            print(e)


async def course_department_with_school(
    department: str, db: asyncpg.Connection
) -> list:
    """Determine which schools have a department with the specified name

    Args:
        department (str): Department
        db (asyncpg.Connection): Database Connection

    Returns:
        list: A list containing string(s) with the name of the schools
    """

    schools = await db.fetch(
        "SELECT school FROM courses WHERE department = $1", department
    )
    schools = list(dict.fromkeys([i["school"] for i in schools]))
    return schools


async def course_codes_department(
    school: str, department: str, db: asyncpg.Connection
) -> list:
    """Fetch course codes given a department and a school

    Args:
        school (str): The school
        department (str): The department
        db (asyncpg.Connection): Database Connection

    Returns:
        list: A list of asyncpg.Record
            (
                code (str): The course code
                name (str): The name of the course
            )
    """

    return await db.fetch(
        "SELECT code, name FROM courses WHERE school = $1 AND department = $2",
        school,
        department.strip().upper(),
    )


async def course_fetch(school: str, course: str, db: asyncpg.Connection):
    """Fetch a course from a course code & school

    Args:
        school (str): The school
        course (str): The course code
        db (asyncpg.Connection): Database Connection

    Returns:
        list: A list of asyncpg.Record
            (
                school (str): The school
                code (str): The course code
                number (int): The course's number
                department (str): The department
                name (str): Name of the course
                description (str): Description of the course
                requirements (str): Requirements to take the course
                academic_level (str): The academic level of the course
                units (float): The units of the course
                campus (str): The campus
            )
    """
    return await db.fetch(
        "SELECT * FROM courses WHERE code = $1 AND school = $2",
        course.strip(),
        school,
    )


async def course_fetch_split(department: str, number: int, db: asyncpg.Connection):
    """Fetch a course given a department & course number

    Args:
        department (str): The department
        number (int): The course's number
        db (asyncpg.Connection): Database Connection

    Returns:
        list: A list of asyncpg.Record
            (
                school (str): The school
                code (str): The course code
                number (int): The course's number
                department (str): The department
                name (str): Name of the course
                description (str): Description of the course
                requirements (str): Requirements to take the course
                academic_level (str): The academic level of the course
                units (float): The units of the course
                campus (str): The campus
            )
    """
    return await db.fetch(
        "SELECT * FROM courses WHERE department = $1 AND number = $2",
        department,
        number,
    )


async def course_department_exist(
    school: str, department: str, db: asyncpg.Connection
) -> bool:
    """Determines if a department exists @ a school

    Args:
        school (str): The school
        department (str): The department
        db (asyncpg.Connection): Database Connection

    Returns:
        bool: Whether the department exists
    """

    result = await db.fetchrow(
        "SELECT EXISTS(SELECT department FROM courses WHERE school = $1 AND department = $2)",
        school,
        department,
    )

    return result["exists"]


async def course_fetch_school(school: str, db: asyncpg.Connection) -> list:
    """Fetches all of the course codes at a school

    Args:
        school (str): The school
        db (asyncpg.Connection): Database Connection

    Returns:
        list: A list of course codes (str)
    """
    raw = await db.fetch("SELECT code FROM courses WHERE school = $1", school)
    codes = [i[0] for i in raw]

    return codes


async def course_fetch_all(course: str, db: asyncpg.Connection) -> dict:
    """Determines all of the schools where a course exists

    Args:
        course (str): A course code
        db (asyncpg.Connection): Database Connection

    Returns:
        dict: Contains key (school) value (asyncpg.Record) pairs.  asyncpg.Record:
            (
                school (str): The school
                code (str): The course code
                number (int): The course's number
                department (str): The department
                name (str): Name of the course
                description (str): Description of the course
                requirements (str): Requirements to take the course
                academic_level (str): The academic level of the course
                units (float): The units of the course
                campus (str): The campus
            )
    """

    schools = ("queens", "uoft", "waterloo")
    results = {}
    for school in schools:
        r = await db.fetchrow(
            "SELECT * FROM courses WHERE school = $1 AND code = $2", school, course
        )

        if r:
            results[school] = r

    return results


async def course_add(
    db: asyncpg.Connection,
    school: str,
    code: str,
    number: int,
    department: str,
    name: str,
    description: str,
    requirements=None,
    academic_level=None,
    units=None,
    campus=None,
):
    """Add a course to the database

    Args:
        db (asyncpg.Connection): Database Connection
        school (str): School
        code (str): Course code
        number (int): Course number
        department (str): Course's department
        name (str): The Course's name
        description (str): The Course's description
        requirements (str): The Course's requirements
        academic_level (str): The academic level of the course (ie. undergrad, grad)
        units (float): The amount of units the course provides
        campus (str): The campus
    """
    if number is not None:
        number = int(number)

    await db.execute(
        "INSERT INTO courses VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
        school,
        code,
        number,
        department,
        name,
        description,
        requirements,
        academic_level,
        units,
        campus,
    )


async def commands_grab(guild_id: int, db: asyncpg.Connection) -> list or False:
    """Fetches all of the commands for the server.

    Args:
        guild_id (int): The Guild's ID
        db (asyncpg.Connection): Database Connection

    Returns:
        list or None: None if there are no commands otherwise a List of Tuples:
            (
                command (str), # The name or denominator for the command
                output (str), # The output message of the command
                image (None or str) # A link to an image to embed in the command
            )
    """
    commands = []

    commands_db = await db.fetch(
        "SELECT command, output, image FROM custom_commands WHERE guild_id = $1",
        guild_id,
    )

    for c in commands_db:
        commands.append((c[0], c[1], c[2]))

    try:
        return commands
    except Exception as e:
        print(e)
        return False


async def command_add(
    name: str, description: str, guild_id: int, db: asyncpg.Connection, image=None
):
    """Add a command to the database.

    Args:
        name (str): The command's name or denominator
        description (str): The command's description
        guild_id (int): The Guild's ID
        db (asyncpg.Connection): Database Connection
        image (str, optional): A link to an image to display
    """

    async with db.transaction():
        try:
            await db.execute(
                "INSERT INTO custom_commands VALUES ($1, $2, $3, $4)",
                guild_id,
                name,
                description,
                image,
            )

        except Exception as e:
            print(e)


async def command_remove(command: str, guild_id: int, db: asyncpg.Connection):
    """Removes a command from the database.

    Args:
        command (str): The command's denominator
        guild_id (int): The Guild's ID
        db (asyncpg.Connection): Database Connection
    """

    async with db.transaction():
        try:
            await db.execute(
                "DELETE FROM custom_commands WHERE guild_id = $1 AND command = $2",
                guild_id,
                command,
            )

        except Exception as e:
            print(e)


async def command_fetch(command: str, guild_id: int, db: asyncpg.Connection):
    """Fetch a command from the database

    Args:
        command (str): The command's denominator
        guild_id (int): The Guild's ID
        db (asyncpg.Connection): Database Connection

    Returns:
        asyncpg.Record:
            (
                command (str): The command's denominator
                output (str): The command's output
                image (str or None): Potentially an image to embed
            )
    """
    return await db.fetchrow(
        "SELECT command, output, image FROM custom_commands WHERE guild_id = $1 AND command = $2",
        guild_id,
        command,
    )


async def welcome_update(guild_id: int, settings: dict, db: asyncpg.Connection):
    """Update the welcome settings for a guild

    Args:
        guild_id (int): The Guild's ID
        settings (dict): The new settings in the form of: {'channel': int, 'message': str, 'enabled': bool}
        db (asyncpg.Connection): Database Connection
    """

    # Check to see if there is already a welcome instance for this guild
    check = await db.fetchrow(
        "SELECT EXISTS(SELECT guild_id FROM welcome WHERE guild_id = $1)",
        guild_id,
    )

    if check[0]:
        await db.execute(
            "UPDATE welcome SET channel = $1, message = $2, enabled = $3 WHERE guild_id = $4",
            settings["channel"],
            settings["message"],
            settings["enabled"],
            guild_id,
        )

    else:
        await db.execute(
            "INSERT INTO welcome VALUES($1, $2, $3, $4)",
            guild_id,
            settings["channel"],
            settings["message"],
            settings["enabled"],
        )


async def welcome_grab(guild_id: int, db: asyncpg.Connection):
    """Fetches a server's welcome settings

    Args:
       guild_id (int): The Guild's ID
       db (asyncpg.Connection): Database Connection

    Returns:
        dict or None: Returns None if there are no settings or the welcome settings in a dictionary:
            {
                'channel': int, # The channel ID where welcome messages are provided.
                'message': str, # The message to welcome a user
                'enabled': bool # Whether welcome messages are enabled.
            }
    """

    data_pull = await db.fetchrow("SELECT * FROM welcome WHERE guild_id = $1", guild_id)

    if data_pull[1] and data_pull[2] and data_pull[3]:
        welcome = {
            "channel": data_pull[1],
            "message": data_pull[2],
            "enabled": data_pull[3],
        }
        return welcome
    else:
        return None


async def settings_grab(guild_id: int, db: asyncpg.Connection):
    """Fetches the server's settings

    Args:
        guild_id (int): The Guild's ID
        db (asyncpg.Connection): Database Connection

    Returns:
        None or dict:
            (
                "programs_channel": int, # The program's verification channel ID
                "course_default_school": str # The default school for course selection
            )
    """

    grab_info = await db.fetchrow(
        "SELECT * FROM settings WHERE guild_id = $1", guild_id
    )

    if grab_info:
        settings = {
            "programs_channel": grab_info[1],
            "course_default_school": grab_info[2],
        }
        return settings
    else:
        return None


async def settings_update(
    guild_id: int, setting: str, new_value, db: asyncpg.Connection
):
    """Update a specific setting

    Args:
        guild_id (int): The Guild's ID
        setting (str): The setting to change
        new_value: The setting's new value
        db (asyncpg.Connection): Database Connection
    """
    await db.execute(
        "UPDATE settings SET $1 = $2 WHERE guild_id = $3",
        setting,
        new_value,
        guild_id,
    )


async def settings_create_default(guild_id: int, db: asyncpg.Connection):
    """Creates the default settings values for a guild

    Args:
        guild_id (int): The Guild's ID
        db (asyncpg.Connection): Database Connection
    """

    async with db.transaction():
        try:
            await db.execute(
                "INSERT INTO settings(guild_id, programs_channel, courses_default_school) VALUES ($1, $2, $3)",
                guild_id,
                None,
                None,
            )

        except Exception as e:
            print(e)
