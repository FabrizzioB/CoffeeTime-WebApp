import asyncssh  # A library to create an SSH tunnel for secure database connections.
import asyncmy  # An async MySQL driver for Python, commonly used with FastAPI.
import sys

# Environment Variables
SSH_HOST = "192.168.56.22"  # IP address of the MySQL server
SSH_PORT = 22
SSH_USER = "vagrant"
SSH_PASSWORD = "vagrant"

DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "coffee_user"
DB_PASSWORD = "coffeeaddict"
DB_NAME = "coffee_db"

# Constants for menu options
SHOW_TEAM_MEMBERS_NAMES = 1
SHOW_MEMBERS_COFFEE = 2
SORT_COFFEE_MEMBER = 3
ADD_COFFEE_MEMBER = 4
ADD_TEAM_MEMBER = 5
EXIT = 6


async def connect_to_db():
    """Establish the connection to the MySQL DB Server via the SSH Tunnel."""
    try:
        # Create the async ssh connection to the server.
        ssh_conn = await asyncssh.connect(
            SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD
        )
        # From the server create the async connection to the DB.
        await ssh_conn.forward_local_port(DB_HOST, DB_PORT, DB_HOST, DB_PORT)
        # Connect to MySQL database
        db_connection = await asyncmy.connect(
            host="127.0.0.1",  # This points to the local machine after the tunnel
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            connect_timeout=10,  # Timeout setting
            read_timeout=60,
        )

        if db_connection:
            return db_connection  # Return the connection for further use

    except asyncssh.Error as ssh_error:
        print(f"SSH Error: {ssh_error}")
        return None  # Return None if the SSH connection fails

    except asyncmy.errors.Error as db_error:
        print(f"MySQL Error: {db_error}")
        return None  # Return None if the MySQL connection fails


async def create_table(connection):
    """Create a table for team members who pay for coffee."""

    if connection is None:
        print("No database connection established.")
        return

    create_table_query = """
    CREATE TABLE IF NOT EXISTS team_members (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        times_paid INT DEFAULT 0
    );
    """

    try:
        async with connection.cursor() as cursor:
            await cursor.execute(create_table_query)
            await connection.commit()
            print("Table 'team_members' created successfully or already exists.\n")
    except asyncmy.errors.Error as e:
        print(f"Error creating table: {e}")
        sys.exit(1)

async def insert_member(connection, name: str, times_paid: int):
    """Insert a new team member into the database."""

    if connection is None:
        print("No database connection established.")
        return

    insert_query = "INSERT INTO team_members (name, times_paid) VALUES (%s, %s);"
    async with connection.cursor() as cursor:
        await cursor.execute(insert_query, (name, times_paid))
        await connection.commit()
        print(f"Inserted member: {name} with {times_paid} coffees.")


async def delete_member(connection, name):
    """Delete a team member from the database."""
    if connection is None:
        print("No database connection established.")
        return False  # Return False to indicate failure

    delete_query = "DELETE FROM team_members WHERE name = (%s);"
    async with connection.cursor() as cursor:
        await cursor.execute(delete_query, (name,))
        await connection.commit()

        # Check how many rows were deleted
        if cursor.rowcount > 0:
            print(f"Deleted member: {name}")
            return True  # Return True to indicate success
        else:
            print(f"No member found with name: {name}")
            return False  # Return False to indicate that no deletion occurred

async def delete_team(connection):
    """Delete a team member from the database."""
    if connection is None:
        print("No database connection established.")
        return False  # Return False to indicate failure

    delete_query = "DELETE FROM team_members;"
    async with connection.cursor() as cursor:
        await cursor.execute(delete_query,)
        await connection.commit()

        # Check how many rows were deleted
        if cursor.rowcount > 0:
            print(f"Team was deleted!")
            return True  # Return True to indicate success
        else:
            print(f"No members are present on the team.")
            return False  # Return False to indicate that no deletion occurred

async def add_one_coffee(connection, name):
    """Increment a new coffee from a member into the database."""

    if connection is None:
        print("No database connection established.")
        return

    insert_query = "UPDATE team_members SET times_paid = times_paid + 1 WHERE name = (%s);"
    async with connection.cursor() as cursor:
        await cursor.execute(insert_query, (name,))
        await connection.commit()
        print(f"Updated times_paid for {name}.")


async def add_multiple_coffees(connection, name: str, number: int):
    """Increment a new coffee from a member into the database."""

    if connection is None:
        print("No database connection established.")
        return False  # Return false indicating failure

    # Check if the number is a positive integer
    if number < 0:
        print("Number of coffees to add cannot be negative.")
        return False  # Return false for invalid input

    insert_query = "UPDATE team_members SET times_paid = times_paid + (%s) WHERE name = (%s);"

    try:
        async with connection.cursor() as cursor:
            await cursor.execute(insert_query, (number, name,))
            await connection.commit()
            print(f"Updated {number} coffees for {name}.")
            return True  # Return true indicating success

    except Exception as e:
        print(f"Error updating coffees for {name}: {str(e)}")
        return False  # Return false indicating failure


async def remove_coffee(connection, name):
    """Remove the coffee count from a specific member in the database."""

    if connection is None:
        print("No database connection established.")
        return

    insert_query = "UPDATE team_members SET times_paid = 0 WHERE name = (%s);"
    async with connection.cursor() as cursor:
        await cursor.execute(insert_query, (name,))
        await connection.commit()
        print(f"Coffee's were deleted for {name}.")

async def show_team_members(connection):
    """Select all team members in alphabetical order."""
    select_query = """
        SELECT * 
        FROM team_members 
        ORDER BY name ASC;
    """

    async with connection.cursor() as cursor:
        await cursor.execute(select_query)
        result = await cursor.fetchall()
        if result:
            # Transform the result into a list of dictionaries for easier readability and JSON serialization
            columns = [col[0] for col in cursor.description]  # Get the column names
            members = [dict(zip(columns, row)) for row in result]
            print(f"Members and their coffee: {members}")
            return members
        else:
            print("No members found.")
            return []  # Return an empty list if no results


async def show_team_members_names(connection):
    """Select all team members' names in alphabetical order."""
    select_query = """
        SELECT name 
        FROM team_members 
        ORDER BY name ASC;
    """

    async with connection.cursor() as cursor:
        await cursor.execute(select_query)
        result = await cursor.fetchall()

        if result:
            # Extract names into a simple list
            member_names = [row[0] for row in result]  # Assuming 'name' is the first column in the row
            print(f"Members names: {member_names}")
            return member_names
        else:
            print("No members found.")
            return []  # Return an empty list if no results


async def sort_least_coffees(connection):
    """Fetch one team member who has paid fewer coffees for the team and order alphabetically."""
    select_query = """
        SELECT name 
        FROM team_members 
        ORDER BY times_paid ASC, name ASC 
        LIMIT 1;
        """

    async with connection.cursor() as cursor:
        await cursor.execute(select_query)
        await connection.commit()

        result = await cursor.fetchone()

        if result:
            print(f"Member with least payments: {result[0]}")
            return result[0]
        else:
            print("No members found.")
            return 1

async def sort_most_coffees(connection):
    """Fetch one team member who has paid fewer coffees for the team and order alphabetically."""
    select_query = """
        SELECT name 
        FROM team_members 
        ORDER BY times_paid DESC, name ASC 
        LIMIT 1;
        """

    async with connection.cursor() as cursor:
        await cursor.execute(select_query)
        await connection.commit()

        result = await cursor.fetchone()

        if result:
            print(f"Member with least payments: {result[0]}")
            return result[0]
        else:
            print("No members found.")
            return 1

async def check_member_exists(connection, name: str) -> bool:
    """Check if a member exists in the database by their name."""
    query = "SELECT COUNT(*) FROM team_members WHERE name = %s;"
    async with connection.cursor() as cursor:
        await cursor.execute(query, (name,))
        result = await cursor.fetchone()
        return result[0] > 0  # Return True if the member exists, else False

async def close_db_connection(connection):
    """Close the database connection gracefully."""

    if connection is None:
        print("No database connection established, can't close what is not opened!")
        return
    elif connection:
        connection.close()
        print("Database connection closed.")
