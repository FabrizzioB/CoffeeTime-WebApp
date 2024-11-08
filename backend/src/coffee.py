import asyncssh     # A library to create an SSH tunnel for secure database connections.
import asyncmy      # An async MySQL driver for Python, commonly used with FastAPI.
import sys
import aiomysql     # Connection pooling creation

# Environment Variables
SSH_HOST = "192.168.58.23"  # IP address of the MySQL server
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

pool = None # Variable to initiate the pool of requests

async def create_db_pool():
    """Establish the connection to the MySQL DB Server via the SSH Tunnel."""
    global pool

    try:
        # Create the async ssh connection to the server.
        ssh_conn = await asyncssh.connect(
            SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD
        )

        # From the server create the async connection to the DB.
        await ssh_conn.forward_local_port(DB_HOST, DB_PORT, DB_HOST, DB_PORT)

        # Connect to MySQL database
        pool = await aiomysql.create_pool(
            host=DB_HOST,  # This points to the local machine after the tunnel
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            minsize=1,  # Minimum number of connections in the pool
            maxsize=10,  # Maximum number of connections in the pool
            autocommit=True  # Auto-commit mode for transactions
        )

        if pool:
            return pool  # Return the connection for further use

    except asyncssh.Error as ssh_error:
        print(f"SSH Error: {ssh_error}")
        return None  # Return None if the SSH connection fails

    except aiomysql.MySQLError as db_error:
        print(f"MySQL Error: {db_error}")
        return None  # Return None if the MySQL connection fails

async def close_db_pool():
    """Close the database connection pool."""
    global pool

    if pool:
        pool.close()
        await pool.wait_closed()
        print("Database connection pool closed.")

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

async def insert_member(name: str, times_paid: int):
    """Insert a new team member into the database."""
    global pool

    if pool is None:
        print("Database connection pool not initialized.")
        return

    insert_query = "INSERT INTO team_members (name, times_paid) VALUES (%s, %s);"

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(insert_query, (name, times_paid))
            await conn.commit()
            print(f"Inserted member {name} with {times_paid} coffees.")


async def delete_member(name):
    """Delete a team member from the database."""
    global pool

    if pool is None:
        print("Database connection pool not initialized.")
        return False  # Return False to indicate failure

    delete_query = "DELETE FROM team_members WHERE name = (%s);"

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(delete_query, (name,))
            # Check how many rows were deleted
            if connection.rowcount > 0:
                print(f"Deleted member: {name}")
                return True  # Return True to indicate success
            else:
                print(f"No member found with name: {name}")
                return False  # Return False to indicate that no deletion occurred

async def delete_team():
    """Delete a team member from the database."""
    global pool

    if pool is None:
        print("Database connection pool not initialized.")
        return False  # Return False to indicate failure

    delete_query = "DELETE FROM team_members;"

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(delete_query,)

            if cursor.rowcount > 0:
                print(f"Team was deleted!")
                return True  # Return True to indicate success
                # Check how many rows were deleted
            else:
                print(f"No members are present on the team.")
                return False  # Return False to indicate that no deletion occurred

async def add_one_coffee(name):
    """Increment a new coffee from a member into the database."""
    global pool

    if pool is None:
        print("No database connection established.")
        return

    insert_query = "UPDATE team_members SET times_paid = times_paid + 1 WHERE name = (%s);"

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(insert_query, (name,))
            await connection.commit()
            print(f"Updated times_paid for {name}.")


async def add_multiple_coffees(name: str, number: int):
    """Increment a new coffee from a member into the database."""
    global pool
    if pool is None:
        print("No database connection established.")
        return False  # Return false indicating failure

    # Check if the number is a positive integer
    if number < 0:
        print("Number of coffees to add cannot be negative.")
        return False  # Return false for invalid input

    insert_query = "UPDATE team_members SET times_paid = times_paid + (%s) WHERE name = (%s);"

    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(insert_query, (number, name,))
                await connection.commit()
                print(f"Updated {number} coffees for {name}.")
                return True  # Return true indicating success

    except Exception as e:
        print(f"Error updating coffees for {name}: {str(e)}")
        return False  # Return false indicating failure


async def remove_coffee(name: str):
    """Remove the coffee count from a specific member in the database."""
    global pool

    if pool is None:
        print("No database connection established.")
        return

    insert_query = "UPDATE team_members SET times_paid = 0 WHERE name = (%s);"

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(insert_query, (name,))
            await connection.commit()
            print(f"Coffee's were deleted for {name}.")

async def show_team_members():
    """Select all team members in alphabetical order."""
    global pool

    select_query = """
        SELECT * 
        FROM team_members 
        ORDER BY name ASC;
    """

    async with pool.acquire() as connection:
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

async def show_team_members_names():
    """Select all team members' names in alphabetical order."""
    global pool

    select_query = """
        SELECT name 
        FROM team_members 
        ORDER BY name ASC;
    """

    async with pool.acquire() as connection:
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


async def sort_least_coffees():
    """Fetch one team member who has paid fewer coffees for the team and order alphabetically."""
    global pool

    if pool is None:
        print("Database connection pool not initialized.")
        return None

    select_query = """
        SELECT name 
        FROM team_members 
        ORDER BY times_paid ASC, name ASC 
        LIMIT 1;
        """

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(select_query)
            result = await cursor.fetchone()

            if result:
                print(f"Member with least payments: {result[0]}")
                return result[0]
            else:
                print("No members found.")
                return 1

async def sort_most_coffees():
    """Fetch one team member who has paid fewer coffees for the team and order alphabetically."""
    global pool

    if pool is None:
        print("Database connection pool not initialized.")
        return None

    select_query = """
        SELECT name 
        FROM team_members 
        ORDER BY times_paid DESC, name ASC 
        LIMIT 1;
        """

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(select_query)
            result = await cursor.fetchone()

            if result:
                print(f"Member with least payments: {result[0]}")
                return result[0]
            else:
                print("No members found.")
                return None

async def check_member_exists(name: str) -> bool:
    """Check if a member exists in the database by their name."""
    global pool

    check_member_exists_query = "SELECT COUNT(*) FROM team_members WHERE name = %s;"

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(check_member_exists_query, (name,))
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
        return
