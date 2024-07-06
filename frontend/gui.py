import streamlit as st
from loguru import logger
import math
from backend.dataset import Dataset
from backend.database import Database
from backend.vectorstore import VectorStore
from configuration import Configuration
import constants
from backend.loader import DocumentLoader
from utils import pretty_print_docs, format_docs

from loguru import logger

class GUI():
    def __init__(self):
        self.dataset = None

    def get_context(self, search_query):
            """Get the context of the search."""
            doc_list = []
            if self.vector_store is not None:
                docs = self.vector_store.database.query_document(search_query)
                for index, (doc, score) in enumerate(docs):
                    logger.info(f"Document {index} score: {score}")
                    doc_list.append(doc)

                pretty_print_docs(doc_list)
            return format_docs(doc_list)

    def run(self):
        image_paths = [
        "https://upload.wikimedia.org/wikipedia/en/7/70/Terminator1984movieposter.jpg",
        "https://upload.wikimedia.org/wikipedia/en/7/70/Terminator1984movieposter.jpg",
        "https://upload.wikimedia.org/wikipedia/en/7/70/Terminator1984movieposter.jpg",
        "https://upload.wikimedia.org/wikipedia/en/7/70/Terminator1984movieposter.jpg",
        "https://upload.wikimedia.org/wikipedia/en/7/70/Terminator1984movieposter.jpg",
        "https://upload.wikimedia.org/wikipedia/en/7/70/Terminator1984movieposter.jpg",
        ]

        num_cols = 4

        num_rows = math.ceil(len(image_paths) / num_cols)
        logger.info(f"num_rows: {num_rows}")

        st.title("Flix Finder")

        # Initialize backend
        self.dataset = Dataset(constants.DB_FILE_LOCATION)
        self.loader = DocumentLoader(Configuration())
        self.vector_store = VectorStore(self.loader, Configuration())
        self.vector_store.init_vectorstore()

        # Inintialize frontend
        columns = self.dataset.get_columns()
        logger.info(f"dataset columns: {columns}")
        logger.info(f"dataset rows: {self.dataset.get_rows()}")

        search_col1, search_col2 = st.columns([4, 1])
        with search_col1:
            search_query = st.text_input("", "Describe movie here...")

        with search_col2:
            search_button = st.button("Search")

        if search_button:
            st.write(f"Searching movies...")
            similar_movies = self.get_context(search_query)
            logger.info(f"similar_movies: {similar_movies}")

        index = 0
        for row in range(num_rows):
            cols = st.columns(num_cols, gap="large") 
            for col in cols:
                if index >= len(image_paths)-1:
                    break
                col.image(image_paths[index], width=200)
                index = index + 1
