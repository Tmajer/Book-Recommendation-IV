from typing import Any

import psycopg2
from psycopg2 import OperationalError
from psycopg2.extensions import connection

import logging
logger = logging.getLogger(__name__)

def create_connection(db_name: str, db_user: str, db_password: str, db_host: str, db_port: str) -> connection:
    conn = None
    try:
        conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
    except OperationalError as e:
        logger.error(f"The error '{e}' occurred")
    return conn

def execute_query(conn: connection, query: str) -> None:
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        cursor.close()
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")

def execute_read_query(conn: connection, query: str) -> list[tuple[Any, ...]]:
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except OperationalError as e:
        print(f"The error '{e}' occurred")
