import json
import os
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_chunks(file_path="processed_texts/cleaned_chunks.json"):
    """Load the cleaned text chunks from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['chunks']

def generate_embeddings(chunks):
    """Generate embeddings for each chunk using OpenAI's API"""
    try:
        client = OpenAI()  # Initialize OpenAI client
        embeddings = []
        
        print("Generating embeddings...")
        for i, chunk in enumerate(chunks):
            # Get embedding for the chunk
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=chunk
            )
            
            # Extract the embedding vector
            embedding = response.data[0].embedding
            embeddings.append(embedding)
            
            # Print progress
            if (i + 1) % 10 == 0 or i==len(chunks)-1:
                print(f"Processed {i + 1}/{len(chunks)} chunks")

        
        return embeddings
    
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return None

def save_embeddings(embeddings, chunks, output_dir="processed_texts"):
    """Save embeddings and their corresponding texts"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "embeddings.json")
    
    # Convert numpy arrays to lists for JSON serialization
    embeddings_list = [embedding.tolist() if isinstance(embedding, np.ndarray) else embedding 
                      for embedding in embeddings]
    
    data = {
        "total_embeddings": len(embeddings),
        "embedding_dim": len(embeddings[0]),
        "data": [
            {
                "chunk": chunk,
                "embedding": emb
            }
            for chunk, emb in zip(chunks, embeddings_list)
        ]
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f)
    
    print(f"Embeddings saved to: {output_path}")
    return output_path