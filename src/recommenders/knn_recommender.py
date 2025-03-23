from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from postgres.postgres_utils import *

import logging
logger = logging.getLogger(__name__)


def create_matrix(conn: connection) -> (csr_matrix, dict[str, int], dict[int, str]):
    logger.debug("Retrieving metadata for matrix construction")
    select_users = "SELECT DISTINCT user_id FROM ratings;"
    logger.debug("Retrieving users")
    user_results = execute_read_query(conn, select_users)
    select_books = "SELECT DISTINCT isbn FROM ratings;"
    logger.debug("Retrieving books")
    book_results = execute_read_query(conn, select_books)
    select_ratings = "SELECT user_id, isbn, book_rating FROM ratings;"
    logger.debug("Retrieving ratings")
    ratings_results = execute_read_query(conn, select_ratings)

    user_rating_count = {}
    book_rating_count = {}
    for rating in ratings_results:
        user_rating_count[rating[0]] = user_rating_count.get(rating[0], 0) + 1
        book_rating_count[rating[1]] = book_rating_count.get(rating[1], 0) + 1

    user_results = [i[0] for i in user_results if user_rating_count[i[0]] > 10]
    book_results = [i[0] for i in book_results if book_rating_count[i[0]] > 5]

    cols = len(user_results)
    rows = len(book_results)
    logger.debug(f"Constructing matrix with shape ({rows}, {cols})")

    user_mapper = dict(zip(user_results, list(range(cols))))
    book_mapper = dict(zip(book_results, list(range(rows))))
    book_inverse_mapper = dict(zip(list(range(rows)), book_results))
    user_index = []
    book_index = []
    ratings = []
    for i in ratings_results:
        if i[0] in user_mapper.keys() and i[1] in book_mapper.keys():
            user_index.append(user_mapper[i[0]])
            book_index.append(book_mapper[i[1]])
            ratings.append(i[2])

    rating_matrix = csr_matrix((ratings, (book_index, user_index)), shape=(rows, cols))
    logger.debug(f"Matrix constructed with shape {rating_matrix.shape}")

    return rating_matrix, book_mapper, book_inverse_mapper


def find_similar_books(isbn: str,
                       rating_matrix: csr_matrix,
                       k: int,
                       book_mapper: dict[str, int],
                       book_inverse_mapper: dict[int, str],
                       metric='cosine',
                       show_distance=False) -> list[str]:
    neighbour_ids = []

    book_ind = book_mapper[isbn]
    book_vec = rating_matrix[book_ind]
    k += 1
    logger.debug(f"Initializing KNN algorithm for k={k}")
    knn = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
    knn.fit(rating_matrix)
    book_vec = book_vec.reshape(1, -1)
    logger.debug(f"Getting neighbors")
    neighbour = knn.kneighbors(book_vec, return_distance=show_distance)
    for i in range(0, k):
        n = neighbour.item(i)
        neighbour_ids.append(book_inverse_mapper[n])
    neighbour_ids.pop(0)
    logger.debug(f"Retrieved {len(neighbour_ids)} neighbors")
    return neighbour_ids


def get_isbn_for_title(conn: connection, title: str, book_mapper: dict[str, int], rating_matrix: csr_matrix) -> str | list[str]:
    title = title.replace("'", "\\'")
    select_books = f"SELECT isbn FROM books WHERE title ILIKE E'{title}';"
    book_results = execute_read_query(conn, select_books)
    if len(book_results) == 0:
        logger.info("Unknown book, retrieving similar ISBNs")
        select_books = f"SELECT title FROM books WHERE title ILIKE E'%{title}%';"
        book_results = execute_read_query(conn, select_books)
        book_results = [f'"{i[0]}"' for i in book_results]
        return book_results
    else:
        logger.info(f"Retrieved {len(book_results)} ISBNs, selecting one with most rating")
        max_ratings = 0
        selected_isbn = ''
        for isbn in [i[0] for i in book_results]:
            if isbn in book_mapper.keys():
                book_ind = book_mapper[isbn]
                isbn_ratings = rating_matrix[book_ind].nnz
                if max_ratings < isbn_ratings:
                    max_ratings = isbn_ratings
                    selected_isbn = isbn
    return selected_isbn


def main():
    conn = create_connection('postgres', 'postgres', 'secret', 'localhost', '5432')
    rating_matrix, book_mapper, book_inverse_mapper = create_matrix(conn)

    initial_book = "The Queen of the Damned (Vampire Chronicles (Paperback))"
    selected_isbn = get_isbn_for_title(conn, initial_book, book_mapper, rating_matrix)

    select_books = "SELECT isbn, title FROM books;"
    book_titles = dict(execute_read_query(conn, select_books))

    similar_isbns = find_similar_books(selected_isbn, rating_matrix, k=20, book_mapper=book_mapper, book_inverse_mapper=book_inverse_mapper)
    book_title = book_titles[selected_isbn]

    recommendations = set()

    logger.info(f"Since you read {book_title} the following books are recommended:")
    for i in similar_isbns:
        if i in book_titles.keys():
            recommendations.add(book_titles[i])
            if len(recommendations) == 5:
                break
    for i, recommendation in enumerate(recommendations):
        logger.info(f"{i+1}. {recommendation}")


if __name__ == '__main__':
    import logging.config
    logging.config.fileConfig('../logging.conf')
    main()