from math import log
from typing import List
from xml.dom.minidom import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader

import constants
import os
from loguru import logger
from configuration import Configuration

class DocumentLoader():
    """Storer class for storing data."""
    def __init__(self, config: Configuration):
        self.config = config

    def load_web_document(self, url):
        """Load a document from a URL."""
        loader = WebBaseLoader(url)
        document = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=constants.CHUNK_SIZE, 
                                                       chunk_overlap=constants.CHUNK_OVERLAP)
        docs = text_splitter.split_documents(document)

        return docs
    
    def load_csv_document(self, csv_location, split_document=False):
        """Load a document from a CSV."""
        logger.info(f"Loading document from {csv_location}...")
        loader = CSVLoader(csv_location)
        document = loader.load()
        logger.info(f"Document loaded from {csv_location}. Total documents: {len(document)}")

        if split_document:
            logger.info(f"Splitting document...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=constants.CHUNK_SIZE, 
                                                        chunk_overlap=constants.CHUNK_OVERLAP)
            docs = text_splitter.split_documents(document)
            logger.info(f"Document split into {len(docs)} parts")
        else:
            docs = document

        return docs
    
    def load_pdf_document(self, pdf_location):
        """Load a document from a PDF."""
        logger.info(f"Loading document from {pdf_location}...")
        loader = PyPDFLoader(pdf_location)
        document = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=constants.CHUNK_SIZE, 
                                                       chunk_overlap=constants.CHUNK_OVERLAP)
        docs = text_splitter.split_documents(document)

        return docs
    
    def load_documents_from_directory(self, doc_location, file_type="pdf"):
        """Load documents from a directory."""
        logger.info(f"Loading documents from location {doc_location}")
        # traverse a directory and get all files of specific type   
        file_names = []
        for root, dirs, files in os.walk(doc_location):
            for file in files:
                logger.info(f"Found file {file}")    
                if file.endswith("." + file_type):
                    file_names.append(os.path.join(root, file))

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=constants.CHUNK_SIZE, 
                                                        chunk_overlap=constants.CHUNK_OVERLAP)
        docs_content = []

        for file in file_names:
            logger.info(f"Splitting document {file}")
            loader = PyPDFLoader(file)
            document = loader.load()
            split_documents = text_splitter.split_documents(document)
            docs_content.extend(split_documents)  
            logger.info(f"Document {file} split into {len(split_documents)} parts")
           
        logger.info(f"Loaded {len(file_names)} documents from location {doc_location}")
        return docs_content