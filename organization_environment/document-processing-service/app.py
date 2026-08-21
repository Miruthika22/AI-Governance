"""
Document Processing Service
Generates embeddings for uploaded documents to support semantic search.
Uses a HuggingFace transformer model for local embedding generation,
with LangChain used to load and chunk documents before embedding.
"""

from transformers import AutoTokenizer, AutoModel
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
model = AutoModel.from_pretrained(EMBEDDING_MODEL_NAME)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def load_and_chunk_document(file_path: str):
    """Loads a document via LangChain and splits it into chunks for embedding."""
    loader = TextLoader(file_path)
    documents = loader.load()
    return text_splitter.split_documents(documents)


def generate_embedding(text: str):
    """Runs the HuggingFace transformer model to produce a document embedding."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)


def process_document_for_search(file_path: str):
    """End-to-end pipeline: load, chunk, and embed a document for search indexing."""
    chunks = load_and_chunk_document(file_path)
    embeddings = [generate_embedding(chunk.page_content) for chunk in chunks]
    return embeddings