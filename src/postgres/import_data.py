from postgres_utils import *
import csv

import logging
import logging.config

def main():
    conn = create_connection('postgres', 'postgres', 'secret', 'localhost', '5432')
    conn.autocommit = True

    logger.info("Importing data into the users table")
    with open('../../data/Users.csv', newline='', encoding='utf-8') as csvfile:
        usersreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(usersreader, None)
        users = []
        for row in usersreader:
            if row[2] == '':
                users.append((row[0], row[1], None))
            else:
                users.append((row[0], row[1], int(float(row[2]))))
        users_string = ", ".join(["%s"] * len(users))
        insert_query = f'INSERT INTO users (user_id, location, age) VALUES {users_string} ON CONFLICT DO NOTHING'

        cursor = conn.cursor()
        cursor.execute(insert_query, users)
        cursor.close()
    logger.info("Imported data into the users table")
    logger.info("Importing data into the books table")
    with open('../../data/Books.csv', newline='', encoding='utf-8') as csvfile:
        booksreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(booksreader, None)
        books = []
        for row in booksreader:
            if row[3] == '':
                books.append((row[0], row[1], row[2], None, row[4]))
            else:
                books.append((row[0], row[1], row[2], int(row[3]), row[4]))
        books_string = ", ".join(["%s"] * len(books))
        insert_query = f'INSERT INTO books (isbn, title, author, year_published, publisher) VALUES {books_string} ON CONFLICT DO NOTHING'

        cursor = conn.cursor()
        cursor.execute(insert_query, books)
        cursor.close()
    logger.info("Imported data into the books table")
    logger.info("Importing data into the ratings table")
    with open('../../data/Ratings.csv', newline='', encoding='utf-8') as csvfile:
        ratingsreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(ratingsreader, None)
        ratings = []
        for row in ratingsreader:
            if row[2] == '':
                ratings.append((row[0], row[1], None))
            else:
                ratings.append((row[0], row[1], int(row[2])))
            if len(ratings) == 10000:
                ratings_string = ", ".join(["%s"] * len(ratings))
                insert_query = f'INSERT INTO ratings (user_id, isbn, book_rating) VALUES {ratings_string} ON CONFLICT DO NOTHING'
                cursor = conn.cursor()
                cursor.execute(insert_query, ratings)
                cursor.close()

                ratings = []

        ratings_string = ", ".join(["%s"] * len(ratings))
        insert_query = f'INSERT INTO ratings (user_id, isbn, book_rating) VALUES {ratings_string} ON CONFLICT DO NOTHING'
        cursor = conn.cursor()
        cursor.execute(insert_query, ratings)
        cursor.close()
    logger.info("Imported data into the ratings table")

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    main()