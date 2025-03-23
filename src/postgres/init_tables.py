from postgres_utils import *


def main():
    conn = create_connection('postgres', 'postgres', 'secret', '20.224.16.50', '5432')

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

    execute_query(conn, create_users_table)
    execute_query(conn, create_books_table)
    execute_query(conn, create_ratings_table)


if __name__ == '__main__':
    main()