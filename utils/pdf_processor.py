import os
import shutil
from typing import Optional
from chromadb.api.models.Collection import Collection

from extract_text_pdf import extract_and_save_text
from clean_text import clean_text, save_cleaned_chunks
from generate_embeddings import generate_embeddings, save_embeddings
from store_embeddings import (
    create_chroma_db, 
    store_embeddings_in_chroma, 
    load_embeddings, 
    clear_vector_db
)

class PDFProcessor:
    def __init__(self):
        self._collection: Optional[Collection] = None
        self._current_pdf_path: Optional[str] = None

    def clear_previous_data(self):
        """Clear all previous processing data"""
        for directory in ["extracted_texts", "processed_texts", "vector_db"]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory)

    def process_pdf(self, pdf_path: str) -> Collection:
        """Process PDF through all steps and return ChromaDB collection"""
        try:
            # Clear previous data
            self.clear_previous_data()
            
            # Store current PDF path
            self._current_pdf_path = pdf_path
            
            # Extract and process text
            extracted_text_path = extract_and_save_text(pdf_path)
            cleaned_chunks = clean_text(extracted_text_path)
            save_cleaned_chunks(cleaned_chunks)
            
            # Generate and store embeddings
            embeddings = generate_embeddings(cleaned_chunks)
            save_embeddings(embeddings, cleaned_chunks)
            
            # Initialize ChromaDB
            embeddings_data = load_embeddings()
            self._collection = store_embeddings_in_chroma(embeddings_data)
            
            return self._collection
            
        except Exception as e:
            self._collection = None
            self._current_pdf_path = None
            raise Exception(f"PDF processing failed: {str(e)}")

    @property
    def collection(self) -> Optional[Collection]:
        return self._collection

    @property
    def current_pdf_path(self) -> Optional[str]:
        return self._current_pdf_path