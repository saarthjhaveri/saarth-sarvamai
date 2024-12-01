import chromadb
import json
import os
import shutil
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

def load_embeddings(file_path="processed_texts/embeddings.json"):
    """Load embeddings and chunks from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['data']

def clear_vector_db(db_path="./vector_db"):
    """Clear the entire vector database directory"""
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        print(f"Cleared existing vector database at {db_path}")
    # Create the directory
    os.makedirs(db_path, exist_ok=True)

def create_chroma_db(collection_name="pdf_qa_collection"):
    """Initialize ChromaDB and create a collection"""
    # Clear existing database and create directory
    db_path = "./vector_db"
    clear_vector_db(db_path)
    
    settings = chromadb.Settings(
        allow_reset=True,
        is_persistent=True,
        persist_directory=db_path
    )
    
    client = chromadb.Client(settings)
    
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-ada-002"
    )
    
    # Create new collection
    try:
        collection = client.get_collection(name=collection_name)
        client.delete_collection(name=collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={"description": "PDF Question Answering Collection"}
    )
    
    return collection

def store_embeddings_in_chroma(embeddings_data, collection_name="pdf_qa_collection"):
    """Store embeddings in ChromaDB"""
    # Create new collection
    collection = create_chroma_db(collection_name)
    
    # Prepare data for insertion
    documents = []  # The text chunks
    embeddings = []  # The embedding vectors
    metadatas = []  # Metadata for each chunk
    ids = []  # Unique IDs for each chunk
    
    for idx, item in enumerate(embeddings_data):
        documents.append(item['chunk'])
        embeddings.append(item['embedding'])
        metadatas.append({"source": "PDF Document"})
        ids.append(f"chunk_{idx}")
    
    # Add data to collection
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Stored {len(documents)} chunks in ChromaDB")
    return collection

def query_similar_chunks(query_text, collection, n_results=3, distance_threshold=0.5):
    """
    Query the database for similar chunks
    Returns a tuple of (results, is_relevant) where is_relevant indicates if the best match is close enough
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Check if we have any results and if the best match (smallest distance) is within threshold
    is_relevant = True
    if results['distances'] and results['distances'][0]:
        best_distance = results['distances'][0][0]
        is_relevant = best_distance <= distance_threshold

    print("is relevant ", is_relevant)
    print("results are ", results)
    
    
    return results, is_relevant