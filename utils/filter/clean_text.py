import re
import json
import os

def clean_text(file_path):
    # Read the text from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Basic text cleaning
    text = re.sub(r'\d+\|', '', text)  # Remove line numbers
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    text = text.strip()
    
    # Split into initial chunks based on section headers
    # Look for patterns like "11.1", "11.2", etc.
    sections = re.split(r'(?=\d+\.\d+\s+[A-Z])', text)
    
    chunks = []
    for section in sections:
        if len(section.strip()) < 50:  # Skip very small sections
            continue
            
        # Further split sections into smaller chunks
        paragraphs = re.split(r'(?<=[.!?])\s+(?=[A-Z])', section)
        
        for para in paragraphs:
            cleaned_para = para.strip()
            # Only keep chunks that are meaningful (not too short and not just headers)
            if len(cleaned_para) > 100 and not cleaned_para.startswith('Fig'):
                # Remove any remaining special characters and normalize whitespace
                cleaned_para = re.sub(r'\s+', ' ', cleaned_para)
                cleaned_para = cleaned_para.lower()  # Convert to lowercase
                chunks.append(cleaned_para)
    
    return chunks

def save_cleaned_chunks(chunks, output_dir="processed_texts"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "cleaned_chunks.json")
    
    data = {
        "total_chunks": len(chunks),
        "chunks": chunks
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned chunks saved to: {output_path}")
    print(f"Total chunks created: {len(chunks)}")
    return output_path

if __name__ == "__main__":
    file_path = 'extracted_texts/ncert_ch11.txt'
    
    # Clean the text and get chunks
    cleaned_chunks = clean_text(file_path)
    
    # Save the cleaned chunks
    output_file = save_cleaned_chunks(cleaned_chunks)
    
    # Print first few chunks to verify
    print("\nFirst few chunks:")
    for i, chunk in enumerate(cleaned_chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(chunk[:200], "...")  # Print first 200 chars of each chunk