from unittest import loader
from loguru import logger
from backend.database import Database
import constants
from backend.dataset import Dataset
from configuration import Configuration, VectorStoreStatus
from backend.loader import DocumentLoader
import os

class VectorStore():
    """Class for storing vectors."""
    vector_db_initialized = False

    def __init__(self, loader: DocumentLoader , config: Configuration) -> None:
        self.loader = loader
        self.config = config
        self.database = Database() 
        
    def init_vectorstore(self):
        database_name = os.path.join(constants.DATASET_FILE.split(".")[0] + ".db")
        logger.info(f"Initializing vector store with database name {database_name}")

        self.config.load_config()
        logger.debug(self.config.get_config())
        logger.debug(f"vector store status = {self.config.get_vector_store_config(database_name).get_vector_store_status()}")

        config_status_good = self.config.get_vector_store_config(database_name).get_vector_store_status() == VectorStoreStatus.READY.value
        db_file_present = self.database.check_db_presence(database_name)

        if not config_status_good:
            logger.info("vector store status not ready as per config file")

        if not db_file_present:
            logger.info(f"vector store database file {database_name} not present")

        if config_status_good and db_file_present:
            self.vector_db_initialized = True
        else:
            self.vector_db_initialized = False

        if not self.vector_db_initialized:
            logger.info("vector store not initialized, initializing...")
            self.database.create_database(database_name)
            docs = self.loader.load_csv_document(constants.DATASET_FILE)
            if len(docs) == 0:
                logger.error("No documents found.")
                return
            
            # Store the documents in the vector store iteratively
            logger.info(f"Adding {len(docs)} documents to vector store...")
            index = 0
            max_docs = constants.MAX_DOCS_TO_LOAD
            while index < len(docs) - max_docs:
                self.database.store_documents(docs[index:index+max_docs])
                logger.info(f"Added {index + max_docs} documents to vector store.")
                index = index + max_docs

            if index < len(docs):
                self.database.store_documents(docs[index:])
                logger.info(f"Added {len(docs)} documents to vector store.")

            logger.info("Done.")
            self.config.get_vector_store_config(database_name).set_vector_store_status(VectorStoreStatus.READY).save_config()  
        else:
            self.database.load_database(database_name)
            logger.info("Vector store already initialized.")