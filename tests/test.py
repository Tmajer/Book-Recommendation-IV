import unittest

from scipy.sparse import csr_matrix

from postgres.postgres_utils import create_connection, execute_read_query
from recommenders.knn_recommender import find_similar_books, get_isbn_for_title


class TestRecommender(unittest.TestCase):

    def test_books_table(self):
        conn = create_connection('postgres', 'postgres', 'secret', 'localhost', '5432')
        initial_book = "The Fellowship of the Ring (The Lord of the Rings, Part 1)"
        initial_book = initial_book.replace("'", "\\'")
        select_books = f"SELECT isbn FROM books WHERE title ILIKE E'{initial_book}';"
        book_results = execute_read_query(conn, select_books)
        isbns_list = [isbn[0] for isbn in book_results]
        self.assertIn("0345339703", isbns_list)
        self.assertIn("0618002227", isbns_list)
        self.assertIn("0618129030", isbns_list)

    def test_users_table(self):
        conn = create_connection('postgres', 'postgres', 'secret', 'localhost', '5432')
        select_users = f"SELECT user_id FROM users;"
        user_results = execute_read_query(conn, select_users)
        user_set = set([i[0] for i in user_results])
        id_set = set([str(i+1) for i in range(len(user_set))])
        self.assertEqual(id_set, user_set)

    def test_find_similar(self):
        isbn = "abc"
        rating_matrix = csr_matrix([[0, 1], [1, 1], [1, 0]])
        k = 1
        book_mapper = {'abc': 0, 'def': 1, 'ghi': 2}
        book_inverse_mapper = {0: 'abc', 1: 'def', 2: 'ghi'}
        res = find_similar_books(isbn, rating_matrix, k, book_mapper, book_inverse_mapper)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], 'def')
        k = 2
        res2 = find_similar_books(isbn, rating_matrix, k, book_mapper, book_inverse_mapper)
        self.assertEqual(len(res2), 2)
        self.assertTrue('def' in res2)
        self.assertTrue('ghi' in res2)

    def test_get_isbn_for_title(self):
        conn = create_connection('postgres', 'postgres', 'secret', 'localhost', '5432')
        title_1 = "Lily Dale : The True Story of the Town that Talks to the Dead"
        book_mapper = {'006008667X': 0}
        rating_matrix = csr_matrix([10, 10, 10, 10, 0, 1, 10])
        self.assertEqual(get_isbn_for_title(conn, title_1, book_mapper, rating_matrix), '006008667X')
        title_2 = "Dale : The True Story of the Town"
        self.assertEqual(get_isbn_for_title(conn, title_2, book_mapper, rating_matrix), [f'"{title_1}"'])

if __name__ == '__main__':
    unittest.main()