import concurrent.futures
import math
import re
import requests
import streamlit as st
from loguru import logger

from backend.dataset import Dataset
from backend.database import Database
from backend.vectorstore import VectorStore
from configuration import Configuration
import constants
from backend.loader import DocumentLoader
from utils import pretty_print_docs, format_docs

logger.remove()
logger.add("gui.log", level="DEBUG", rotation="500MB")

HEADERS = {
    'User-Agent': 'FlixFinder/1.0 (your-devgaonkar@gmail.com)'
}

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif')


def is_valid_image_url(url: str) -> bool:
    """Fast local sanity check on image URL format."""
    if not url or "%7C" in url or "|" in url or "=" in url:
        return False
    clean = url.split("?")[0].lower()
    return any(clean.endswith(ext) for ext in IMAGE_EXTENSIONS)


@st.cache_data(ttl=86400, show_spinner=False)
def verify_image_url(url: str) -> str:
    """Verify image URL exists using lightweight HEAD request with fallback."""
    if not is_valid_image_url(url):
        return constants.DEFAULT_MOVIE_POSTER

    try:
        res = requests.head(url, headers=HEADERS, timeout=1.5, allow_redirects=True)
        if res.status_code == 200:
            return url
    except Exception:
        pass

    if "en/" in url:
        commons_url = url.replace("en/", "commons/")
        try:
            res = requests.head(commons_url, headers=HEADERS, timeout=1.5, allow_redirects=True)
            if res.status_code == 200:
                return commons_url
        except Exception:
            pass

    return "ERR0R_NO_IMAGE_FOUND.jpg"


def batch_resolve_posters(image_paths):
    """Resolve poster URLs concurrently to eliminate sequential network blocking."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(verify_image_url, image_paths))


@st.cache_resource(show_spinner="Loading movie recommendation model...")
def get_backend():
    """Cache dataset, loader, and vectorstore as singletons across all user sessions."""
    logger.info("Initializing backend resources (singleton)...")
    dataset = Dataset(constants.DATASET_FILE)
    loader = DocumentLoader(Configuration())
    vector_store = VectorStore(loader, Configuration())
    vector_store.init_vectorstore()
    logger.info("Backend resources initialized.")
    return dataset, loader, vector_store


@st.cache_data(show_spinner=False)
def search_similar_content(_vector_store, search_query: str):
    """Cache semantic query results to make common/default queries instantaneous."""
    doc_list = []
    if _vector_store is not None:
        docs = _vector_store.database.query_document(search_query)
        for index, (doc, score) in enumerate(docs):
            logger.debug(f"Document {index} score: {score}")
            doc_list.append(doc.page_content)
    return doc_list


class GUI():
    def __init__(self):
        self.num_cols = constants.NUM_COLUMNS
        self.dataset, self.loader, self.vector_store = get_backend()

    def print_movie_names(self, movie_data):
        """Print the movie names."""
        for movie in movie_data:
            match = re.search(r"noriginal_title:\s+(.*)\n", movie)
            if match:
                logger.info(f"Movie: {match.group(1)}")

    def get_similar_content(self, search_query):
        """Get the context of the search with caching."""
        return search_similar_content(self.vector_store, search_query)

    def update_movie_recommendations(self, movie_data):
        """Update the movie recommendations."""
        poster_images = []
        movie_names = []
        for movie in movie_data:
            match = re.search(r"poster:\s+(.*)", movie)
            if match:
                poster_images.append(match.group(1).strip())
            else:
                poster_images.append("")

            match = re.search(r"title:\s+(.*)", movie)
            if match:
                movie_names.append(match.group(1).strip())
            else:
                movie_names.append("Unknown Title")

        self.update_movie_posters(poster_images, movie_names)

    def update_movie_posters(self, image_paths, movie_names):
        """Update the movie posters."""
        logger.info(f"Updating movie posters: {len(image_paths)} movies")
        num_rows = math.ceil(len(image_paths) / self.num_cols)

        resolved_images = batch_resolve_posters(image_paths)

        st.session_state.poster_container.empty()
        with st.session_state.poster_container.container():
            index = 0
            for row in range(num_rows):
                cols = st.columns(self.num_cols, gap="small", vertical_alignment="bottom")
                for col in cols:
                    if index >= len(resolved_images):
                        break
                    caption = movie_names[index]
                    wiki_link = f"https://en.wikipedia.org/wiki/{caption.replace(' ', '_')}"
                    poster_url = resolved_images[index]

                    col.image(poster_url, use_column_width=True)
                    col.markdown(f"[{caption}]({wiki_link})")
                    index += 1

    def run(self):
        st.set_page_config(page_title="Flix Finder", page_icon="🐰", layout="wide")

        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

        st.title("Flix Finder")

        with st.container(border=True):
            search_col1, search_col2 = st.columns([4, 1], gap="small", vertical_alignment="center")
            with search_col1:
                search_query = st.text_input("", "", label_visibility="collapsed", key="search_query")

            with search_col2:
                search_button = st.button("Search")

        self.poster_container = st.empty()
        st.session_state.poster_container = self.poster_container

        if search_button and "search_query" in st.session_state and st.session_state.search_query.strip():
            query = st.session_state.search_query.strip()
            similar_movies = self.get_similar_content(query)
            self.print_movie_names(similar_movies)
            self.update_movie_recommendations(similar_movies)
        elif "search_query" in st.session_state and st.session_state.search_query.strip():
            similar_movies = self.get_similar_content(st.session_state.search_query.strip())
            self.update_movie_recommendations(similar_movies)
        else:
            default_movies = self.get_similar_content("horror movies with zombies")
            self.update_movie_recommendations(default_movies)
