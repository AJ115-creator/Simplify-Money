from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
import os
from dotenv import load_dotenv
import torch

load_dotenv()

# Initialize sentence transformer for semantic understanding
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize lightweight LLM (82M parameters) with optimizations
model_name = "distilgpt2"  
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(
    model_name, 
    torch_dtype=torch.float16,  # Use half-precision for memory efficiency
    low_cpu_mem_usage=True,     # Optimize CPU memory usage
    device_map='auto'           # Automatic device selection
)

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=-1
)

def index_csv_content(content: list) -> list:
    """
    Create embeddings for CSV content for semantic search capability
    Args:
        content: List of dictionaries containing CSV data
    Returns:
        List of embeddings for each row
    """
    # Convert list of dicts to string for embedding
    texts = [" ".join([f"{k}: {v}" for k, v in row.items()]) for row in content]
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

def format_csv_content(content: list) -> str:
    """
    Format CSV content into a readable string for the LLM
    Args:
        content: List of dictionaries containing CSV data
    Returns:
        Formatted string representation of CSV data
    """
    # Format the CSV content as a readable string
    rows = []
    if content:
        headers = list(content[0].keys())
        rows.append("Headers: " + ", ".join(headers))
        for row in content:
            row_str = " | ".join([f"{k}: {v}" for k, v in row.items()])
            rows.append(row_str)
    return "\n".join(rows)

def query_csv(file_content: list, query: str) -> str:
    """
    Process natural language queries on CSV data
    Args:
        file_content: List of dictionaries containing CSV data
        query: Natural language query string
    Returns:
        Generated response from the LLM
    """
    try:
        # Format only relevant parts of the CSV to reduce context
        formatted_content = format_csv_content(file_content[:10])  # Limit to first 10 rows
        
        prompt = f"""Analyze this CSV data preview and answer the query.
Data Preview:
{formatted_content}

Query: {query}
Analysis: """
        
        response = generator(
            prompt,
            max_length=150,  # Keep responses short
            min_length=20,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id
        )
        
        return response[0]['generated_text'].split('Analysis:')[-1].strip()
        
    except Exception as e:
        return f"Error processing query: {str(e)}"
