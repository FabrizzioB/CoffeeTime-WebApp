"""Methods to access the database"""

import sys
from backend.src.app.db.connection import get_db_pool


async def insert_member(name: str, coffees: int):
    """Insert a new team member."""
    pool = get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO team_members (name, coffees) VALUES (%s, %s)", (name, coffees))
            await conn.commit()


async def check_member_exists(name: str) -> bool:
    """Check if a member exists in the database by their name."""
    pool = get_db_pool()
    check_member_exists_query = "SELECT COUNT(*) FROM team_members WHERE name = %s;"
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(check_member_exists_query, (name,))
            result = await cursor.fetchone()
            return result[0] > 0  # Return True if the member exists, else False


async def update_coffee(name: str, number: int):
    """Increment a coffee count for a member."""
    pool = get_db_pool()
    if await check_member_exists(name):
        if number < 0:
            print("Number of coffees to add cannot be negative.")
            return False

        update_query = "UPDATE team_members SET times_paid = %s WHERE name = %s;"
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(update_query, (number, name))
                await connection.commit()
                print(f"Updated {number} coffees for {name}.")
                return True
    else:
        print(f"Member '{name}' does not exist.")
        return False


async def delete_member(name: str):
    """Delete a team member."""
    pool = get_db_pool()
    if await check_member_exists(name):
        delete_query = "DELETE FROM team_members WHERE name = %s;"
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(delete_query, (name,))
                if cursor.rowcount > 0:
                    print(f"Deleted member: {name}")
                    return True
    print(f"No member found with name: {name}")
    return False


async def delete_entire_team():
    """Delete all members from the team."""
    pool = get_db_pool()
    delete_query = "DELETE FROM team_members;"
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(delete_query)
            if cursor.rowcount > 0:
                print("Deleted all team members.")
                return True
            else:
                print("No team members to delete.")
                return False


async def show_team_members():
    """Fetch all team members."""
    pool = get_db_pool()
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
                columns = [col[0] for col in cursor.description]
                members = [dict(zip(columns, row)) for row in result]
                print(f"Members and their coffee: {members}")
                return members
            else:
                print("No members found.")
                return []


async def sort_least_coffees():
    """Fetch the member with the least coffees paid."""
    pool = get_db_pool()
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
            return result[0] if result else None


async def sort_most_coffees():
    """Fetch the member with the most coffees paid."""
    pool = get_db_pool()
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
            return result[0] if result else None
