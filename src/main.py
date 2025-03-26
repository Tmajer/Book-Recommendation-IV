from fastapi import FastAPI
import yaml

from starlette.responses import FileResponse

from postgres.postgres_utils import create_connection, execute_read_query
from recommenders.knn_recommender import create_matrix, get_isbn_for_title, find_similar_books

import logging
import logging.config

logging.config.fileConfig('./src/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = FastAPI()
config = yaml.safe_load(open("./src/config.yml"))

@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse('./src/pages/index.html')

@app.get("/recommend/{book_name}")
def read_item(book_name: str) -> dict[str, str]:
    conn = create_connection(config['db_name'], config['user'], config['password'], config['url'], config['port'])
    if conn is None:
        logger.error("System could not connect to the database")
        return {"message": "System could not connect to the book database, please try again later."}
    rating_matrix, book_mapper, book_inverse_mapper, book_rating_count = create_matrix(conn)
    logger.info(f"Retrieving ISBN for {book_name}")
    selected_isbn = get_isbn_for_title(conn, book_name, book_mapper, rating_matrix)

    if type(selected_isbn) is list and 0 < len(selected_isbn):
        return {"message": f"We could not find {book_name} in our database. Try inputting one of the following books:\n\n{'\n'.join(selected_isbn[:min(len(selected_isbn), 10)])}"}
    elif type(selected_isbn) is list:
        return {"message": f"We could not find {book_name} or any similar book titles in our database."}
    elif selected_isbn == '':
        return {"message": f"We could not find any books similar to {book_name}, try inputing a different book."}

    select_books = "SELECT isbn, title FROM books;"
    book_titles = dict(execute_read_query(conn, select_books))

    similar_isbns = find_similar_books(selected_isbn, rating_matrix, k=20, book_mapper=book_mapper,
                                       book_inverse_mapper=book_inverse_mapper)
    recommendations = set()

    for i in similar_isbns:
        if i in book_titles.keys() and book_rating_count[i] >= 5 and book_titles[i] != book_name:
            recommendations.add(book_titles[i])
            if len(recommendations) == 5:
                break
    if len(recommendations) < 5:
        for i in similar_isbns:
            if i in book_titles.keys() and book_titles[i] != book_name:
                recommendations.add(book_titles[i])
                if len(recommendations) == 5:
                    break

    output = f"Since you read {book_name}, you might also like:\n"
    for i, recommendation in enumerate(recommendations):
        output += f"{i + 1}. {recommendation}\n"
    return {"message": output}