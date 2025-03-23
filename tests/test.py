import unittest

from scipy.sparse import csr_matrix

from postgres.postgres_utils import create_connection
from recommenders.knn_recommender import find_similar_books, get_isbn_for_title


class TestRecommender(unittest.TestCase):

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