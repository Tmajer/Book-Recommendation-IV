import numpy as np
from scipy.constants import value

from postgres.postgres_utils import *

def main():
    conn = create_connection('postgres', 'postgres', 'secret', 'localhost', '5432')

    initial_book = "The Fellowship of the Ring (The Lord of the Rings, Part 1)"
    initial_book = initial_book.replace("'", "\\'")

    select_books = f"SELECT isbn FROM books WHERE title ILIKE E'{initial_book}';"
    book_results = execute_read_query(conn, select_books)
    print(f"Number of books similar to name: {len(book_results)}")
    if len(book_results) == 0:
        select_books = f"SELECT title FROM books WHERE title ILIKE '%{initial_book}%';"
        book_results = execute_read_query(conn, select_books)
        book_results = [f'"{i[0]}"' for i in book_results]
        print(f"Did you mean one of the following? {', '.join(book_results)}")
        return

    isbns = [f"'{r[0]}'" for r in book_results]
    select_users_and_ratings = f"SELECT user_id , book_rating FROM ratings WHERE isbn IN ({', '.join(isbns)});"
    user_and_ratings_results = execute_read_query(conn, select_users_and_ratings)

    user_rating_med = np.median([r[1] for r in user_and_ratings_results if r[1] > 0])

    user_ids = [f"'{r[0]}'" for r in user_and_ratings_results if r[1] >= user_rating_med]
    print(f"Number of selected users: {len(user_ids)}")

    select_user_ratings = f"SELECT user_id , isbn , book_rating FROM ratings WHERE user_id IN ({', '.join(user_ids)}) AND isbn NOT IN ({', '.join(isbns)});"
    user_ratings_results = execute_read_query(conn, select_user_ratings)

    book_set = set()
    user_set = set()
    user_rating_count = {}
    for user_rating in user_ratings_results:
        book_id = user_rating[1]
        if not book_id in book_set:
            book_set.add(book_id)
        user_id = user_rating[0]
        if not user_id in user_set:
            user_rating_count[user_id] = user_rating_count.get(user_id, 0) + 1
            if user_rating_count[user_id] >= 10:
                user_set.add(user_id)

    book_score = {}

    for user_rating in user_ratings_results:
        user_id = user_rating[0]
        book_id = user_rating[1]
        rating = user_rating[2]
        if user_id in user_set and book_id in book_set:
            scores = book_score.get(book_id, [])
            if rating != 0:
                scores.append(rating)
                book_score[book_id] = scores

    average_book_score = {}
    median_rating_count = np.median([len(v) for v in book_score.values()])
    for book, bratings in book_score.items():
        if len(bratings) > median_rating_count:
            average_book_score[book] = np.average(bratings)

    recommendation_isbns = [f"'{isbn}'" for isbn in sorted(average_book_score, key=average_book_score.get, reverse=True)[:10]]
    select_recommendations = f"SELECT DISTINCT ON (title) title , author , isbn FROM books WHERE isbn IN ({', '.join(recommendation_isbns)});"
    recommendations_results = execute_read_query(conn, select_recommendations)
    recommendations_results.sort(key=lambda x: recommendation_isbns.index(f"'{x[2]}'"))

    for result in recommendations_results:
        print(f"{result[0]}, {result[1]}")


if __name__ == '__main__':
    main()
