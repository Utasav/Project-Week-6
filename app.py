from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from striprtf.striprtf import rtf_to_text  # Library for reading RTF files

app = Flask(__name__)

# Path to the folder with the RTF documents
doc_folder = r"C:\News documents\Week 6 NEWS Documents"

# Function to read the content of an RTF document
def read_rtf_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        rtf_content = file.read()
    return rtf_to_text(rtf_content)

# Load documents from the folder
documents = []
document_content = []

# Debugging: Check if the directory exists and print its contents
if not os.path.exists(doc_folder):
    print(f"Error: The folder '{doc_folder}' does not exist.")
    raise ValueError(f"Folder '{doc_folder}' does not exist.")
else:
    print(f"Folder '{doc_folder}' found. Listing files...")

files_in_directory = os.listdir(doc_folder)
if not files_in_directory:
    print(f"Error: The folder '{doc_folder}' is empty.")
    raise ValueError(f"Folder '{doc_folder}' is empty.")
else:
    print(f"Files found: {files_in_directory}")

# Process RTF documents and add debug print statements
for filename in files_in_directory:
    if filename.endswith(".rtf"):
        file_path = os.path.join(doc_folder, filename)
        print(f"Processing file: {file_path}")  # Debug: Show which file is being processed
        try:
            content = read_rtf_file(file_path)  # Read the content of the RTF document
            if content.strip():  # Ensure the document is not empty
                documents.append(filename)  # Add the document name
                document_content.append(content)
                print(f"Successfully read file: {filename}")  # Debug: Confirm file was read
            else:
                print(f"Warning: File '{filename}' is empty.")  # Debug: Warn if file is empty
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# If no documents were processed, raise an error
if not documents:
    raise ValueError("No valid documents to process.")

# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer()
doc_vectors = vectorizer.fit_transform(document_content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    
    # Check if the query is empty
    if not query.strip():
        return render_template('result.html', query=query, results=[], error="Please enter a valid search query.")
    
    query_vector = vectorizer.transform([query])

    # Compute cosine similarity
    similarity_scores = cosine_similarity(query_vector, doc_vectors).flatten()

    # Get top 5 most similar documents
    top_indices = similarity_scores.argsort()[-5:][::-1]
    results = [
        {"title": documents[i], "relevance": round(similarity_scores[i] * 100, 2), "snippet": document_content[i][:200]}
        for i in top_indices
    ]

    return render_template('result.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
