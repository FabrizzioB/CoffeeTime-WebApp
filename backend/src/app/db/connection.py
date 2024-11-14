import aiomysql
from backend.src.app.utils.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

pool = None

async def create_db_pool():
    global pool
    pool = await aiomysql.create_pool(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, db=DB_NAME
    )

async def close_db_pool():
    global pool
    pool.close()
    await pool.wait_closed()
