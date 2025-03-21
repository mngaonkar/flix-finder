import urllib.request
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
import urllib
import requests
from loguru import logger
import sys

logger.remove()
logger.add("gui.log", level="DEBUG", rotation="500MB")

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
        logger.info(movie_data)
        poster_images = []
        movie_names = []
        for movie in movie_data:
            match = re.search(r"poster:\s+(.*)", movie)
            logger.info(f"Poster: {match.group(1)}")
            if match:
                poster_images.append(match.group(1))
            match = re.search(r"title:\s+(.*)", movie)
            if match:
                logger.info(f"Movie: {match.group(1)}")
                movie_names.append(match.group(1))
            match = re.search(r"plot:\s+(.*)", movie)
            if match:
                logger.info(f"Plot: {match.group(1)}")
        self.update_movie_posters(poster_images, movie_names)
        
        
    def run(self):
        st.set_page_config(page_title="Flix Finder", page_icon="🐰", layout="wide")

        # Hide the Streamlit menu and footer
        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
       
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
                search_query = st.text_input("", "", label_visibility="collapsed", key="search_query")

            with search_col2:
                search_button = st.button("Search")

        if search_button:
            st.write(f"Searching movies...")
            if "search_query" in st.session_state:
                similar_movies = self.get_similar_content(st.session_state.search_query)
                logger.info(f"similar_movies: {similar_movies}")
                self.print_movie_names(similar_movies)
                self.update_movie_recommendations(similar_movies)

        self.poster_container = st.empty()
        st.session_state.poster_container = self.poster_container
        if "search_query" in st.session_state and st.session_state.search_query != "":
            logger.info(f"search_query: {st.session_state.search_query}")
            random_movies = self.get_similar_content(st.session_state.search_query)
        else:
            random_movies = self.get_similar_content("horror movies with zombies")
        self.update_movie_recommendations(random_movies)

    def update_movie_posters(self, image_paths, movie_names):
        """Update the movie posters."""
        logger.info(f"Updating movie posters: {image_paths}")
        num_rows = math.ceil(len(image_paths) / self.num_cols)

        headers = {
            'User-Agent': 'FlixFinder/1.0 (your-devgaonkar@gmail.com)'
        }
        
        st.session_state.poster_container.empty()
        with st.session_state.poster_container.container():
            index = 0
            for row in range(num_rows):
                cols = st.columns(self.num_cols, gap="small", vertical_alignment="bottom") 
                for col in cols:
                    if index >= len(image_paths):
                        break
                    caption = movie_names[index]
                    wiki_link = f"https://en.wikipedia.org/wiki/{caption.replace(' ', '_')}"

                    if image_paths[index] == "":
                        col.image(constants.DEFAULT_MOVIE_POSTER, use_column_width=True)
                    else:
                        try:
                            response = requests.get(image_paths[index], headers=headers)
                            if response.status_code != 200:
                                raise Exception(f"Image {image_paths[index]} not found")
                            col.image(image_paths[index], use_column_width=True)
                            col.markdown(f"[{caption}]({wiki_link})")
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            try:
                                image_paths[index] = image_paths[index].replace("en/", "commons/")
                                response = requests.get(image_paths[index], headers=headers)
                                if response.status_code != 200:
                                    raise Exception(f"Image {image_paths[index]} not found")
                                
                                col.image(image_paths[index], use_column_width=True, output_format="auto")
                                col.markdown(f"[{caption}]({wiki_link})")
                            except Exception as e:
                                logger.error(f"Error: {e}")
                                col.image("ERR0R_NO_IMAGE_FOUND.jpg", use_column_width=True, output_format="auto")
                                col.markdown(f"[{caption}]({wiki_link})")
                    index = index + 1
