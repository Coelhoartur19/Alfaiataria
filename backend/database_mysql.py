from typing import Generator
from mysql.connector import MySQLConnection
import mysql.connector


def get_db() -> Generator[MySQLConnection, None, None]:
    conn: MySQLConnection = mysql.connector.connect(
        host="26.130.166.26",
        user="david",
        password="beckgerencia!",
        database="alfaiataria"
        
    )
    try:
        yield conn
    finally:
        conn.close()
