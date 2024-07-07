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
import re

from loguru import logger

class GUI():
    def __init__(self):
        self.dataset = None
        self.num_cols = constants.NUM_COLUMNS

    def print_movie_names(self, movie_data):
        """Print the movie names."""
        for movie in movie_data:
            match = re.search(r"noriginal_title:\s+(.*)\n", movie)
            if match:
                logger.info(f"Movie: {match.group(1)}")

    def get_similar_content(self, search_query):
            """Get the context of the search."""
            doc_list = []
            if self.vector_store is not None:
                docs = self.vector_store.database.query_document(search_query)
                for index, (doc, score) in enumerate(docs):
                    logger.info(f"Document {index} score: {score}")
                    doc_list.append(doc.page_content)

                # pretty_print_docs(doc_list)
            return doc_list

    def update_movie_recommendations(self, movie_data):
        """Update the movie recommendations."""
        poster_images = []
        for movie in movie_data:
            match = re.search(r"PosterLink:\s+(.*)", movie)
            if match:
                poster_images.append(match.group(1))
            match = re.search(r"original_title:\s+(.*)", movie)
            if match:
                logger.info(f"Movie: {match.group(1)}")
        self.update_movie_posters(poster_images)
        
        
    def run(self):
        st.set_page_config(page_title="Flix Finder", page_icon="", layout="wide")
        st.title("Flix Finder")

        # Initialize backend
        self.dataset = Dataset(constants.DATASET_FILE)
        self.loader = DocumentLoader(Configuration())
        self.vector_store = VectorStore(self.loader, Configuration())
        self.vector_store.init_vectorstore()

        # Inintialize frontend
        columns = self.dataset.get_columns()
        logger.info(f"dataset columns: {columns}")
        logger.info(f"dataset rows: {self.dataset.get_rows()}")

        with st.container(border=True):
            search_col1, search_col2 = st.columns([4, 1], gap="small", vertical_alignment="center")
            with search_col1:
                search_query = st.text_input("", "horror movies with zombies", label_visibility="collapsed", key="search_query")

            with search_col2:
                search_button = st.button("Search")

        if search_button:
            st.write(f"Searching movies...")
            if "search_query" in st.session_state:
                similar_movies = self.get_similar_content(st.session_state.search_query)
                # logger.info(f"similar_movies: {similar_movies}")
                self.print_movie_names(similar_movies)
                self.update_movie_recommendations(similar_movies)

        self.poster_container = st.empty()
        st.session_state.poster_container = self.poster_container
        random_movies = self.get_similar_content("horror movies with zombies")
        self.update_movie_recommendations(random_movies)

    def update_movie_posters(self, image_paths):
        """Update the movie posters."""
        logger.info(f"Updating movie posters: {image_paths}")
        num_rows = math.ceil(len(image_paths) / self.num_cols)
        st.session_state.poster_container.empty()
        with st.session_state.poster_container.container():
            index = 0
            for row in range(num_rows):
                cols = st.columns(self.num_cols, gap="small") 
                for col in cols:
                    if index >= len(image_paths):
                        break
                    if image_paths[index] == "":
                        col.image(constants.DEFAULT_MOVIE_POSTER, use_column_width=True)
                    else:
                        col.image(image_paths[index], use_column_width=True)
                    index = index + 1