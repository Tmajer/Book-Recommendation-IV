from postgres_utils import *

import logging
import logging.config

def main():
    conn = create_connection('postgres', 'postgres', 'secret', 'localhost', '5432')

    create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
          user_id TEXT PRIMARY KEY,
          location TEXT,
          age INTEGER
        )
        """
    create_books_table = """
        CREATE TABLE IF NOT EXISTS books (
          isbn TEXT PRIMARY KEY,
          title TEXT,
          author TEXT,
          year_published INTEGER,
          publisher TEXT
        )
        """
    create_ratings_table = """
        CREATE TABLE IF NOT EXISTS ratings (
          user_id TEXT REFERENCES users(user_id),
          isbn TEXT,
          book_rating INTEGER,
          PRIMARY KEY (user_id, isbn)
        )
        """

    logger.info("Creating users table")
    execute_query(conn, create_users_table)
    logger.info("Creating books table")
    execute_query(conn, create_books_table)
    logger.info("Creating ratings table")
    execute_query(conn, create_ratings_table)


if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    main()