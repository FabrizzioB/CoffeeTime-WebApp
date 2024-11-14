"""Methods to access the database"""

import sys
import asyncmy      # An async MySQL driver for Python, commonly used with FastAPI
import aiomysql     # Connection pooling creation

from backend.src.app.utils.config import *
from backend.src.app.db.connection import pool

pool = None # Variable to initiate the pool of requests

async def insert_member(name: str, coffees: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO team_members (name, coffees) VALUES (%s, %s)", (name, coffees))
            await conn.commit()

async def create_db_pool():
    """Establish the connection to the MySQL DB Server via the SSH Tunnel."""
    global pool

    try:
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
            print("Database pool connection created successfully.")
            return pool  # Return the connection for further use

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


async def close_db_connection(connection):
    """Close the database connection gracefully."""

    if connection is None:
        print("No database connection established, can't close what is not opened!")
        return
    elif connection:
        connection.close()
        print("Database connection closed.")
        return


async def check_member_exists(name: str) -> bool:
    """Check if a member exists in the database by their name."""
    global pool
    check_member_exists_query = "SELECT COUNT(*) FROM team_members WHERE name = %s;"
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(check_member_exists_query, (name,))
            result = await cursor.fetchone()
            return result[0] > 0  # Return True if the member exists, else False

async def insert_member(name: str, times_paid: int):
    """Insert a new team member into the database."""
    global pool
    if pool is None:
        print("Database connection pool not initialized.")
        return

    insert_query = "INSERT INTO team_members (name, times_paid) VALUES (%s, %s);"

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Check if the member exists
            if await check_member_exists(name):
                print(f"Member '{name}' already exists.")
                return

            # Insert new member if it does not exist
            await cursor.execute(insert_query, (name, times_paid))
            await conn.commit()
            print(f"Inserted member {name} with {times_paid} coffees.")

async def update_coffee(name: str, number: int):
    """Increment a new coffee from a member into the database."""
    global pool

    if pool is None:
        print("No database connection established.")
        return False  # Return false indicating failure

    # Check if the member exists
    if await check_member_exists(name):
        # Check if the number is a positive integer
        if number < 0:
            print("Number of coffees to add cannot be negative.")
            return False  # Return false for invalid input

        insert_query = "UPDATE team_members SET times_paid = (%s) WHERE name = (%s);"

        try:
            async with pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(insert_query, (number, name,))
                    await connection.commit()
                    print(f"Updated {number} coffees for {name}.")
                    return True  # Return true indicating success
        except Exception as e:
            print(f"Some error occurred while updating the coffees for {name}: {str(e)}")
            return False  # Return false indicating failure

async def delete_member(name):
    """Delete a team member from the database."""
    global pool

    if pool is None:
        print("Database connection pool not initialized.")
        return False  # Return False to indicate failure

    if await check_member_exists(name):
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

async def delete_entire_team():
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
        ORDER BY times_paid ASC, id ASC 
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
