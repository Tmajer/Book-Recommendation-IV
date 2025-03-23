from postgres_utils import *
import csv

def main():
    conn = create_connection('postgres', 'postgres', 'secret', '20.224.16.50', '5432')
    conn.autocommit = True

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

if __name__ == '__main__':
    main()