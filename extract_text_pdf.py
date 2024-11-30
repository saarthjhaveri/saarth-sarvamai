import PyPDF2
import os

def extract_and_save_text(pdf_path, output_dir="extracted_texts"):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate output filename from PDF filename
    pdf_filename = os.path.basename(pdf_path)
    txt_filename = os.path.splitext(pdf_filename)[0] + ".txt"
    output_path = os.path.join(output_dir, txt_filename)
    
    # Extract text from PDF
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    
    # Save text to file
    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    
    print(f"Text extracted and saved to: {output_path}")
    return output_path