"""Testing the connection to the Docker container"""
import pymysql

from backend.src.app.utils.config import *

try:
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print("Connection successful to MySQL!")
    connection.close()
except pymysql.MySQLError as e:
    print(f"Error when trying to connect to MySQL: {e}")
