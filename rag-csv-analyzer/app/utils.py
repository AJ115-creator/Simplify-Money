import uuid
import pandas as pd
import os
from fastapi import HTTPException
import io

def generate_file_id():
    return str(uuid.uuid4())

def validate_csv_file(file):
    try:
        # First try standard CSV reading
        try:
            df = pd.read_csv(file)
        except pd.errors.ParserError:
            # If that fails, try with Python engine and auto separator detection
            if hasattr(file, 'seek'):
                file.seek(0)
            df = pd.read_csv(file, sep=None, engine='python')
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        if len(df.columns) < 1:
            raise HTTPException(status_code=400, detail="CSV file has no columns")
            
        # Clean the DataFrame
        df = df.fillna('')  # Replace NaN with empty string
        
        return df
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

def process_uploaded_file(file):
    df = validate_csv_file(file)
    return df.to_dict(orient="records")

def read_csv_file(file_path: str) -> list:
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
    with open(file_path, 'rb') as f:
        df = validate_csv_file(f)
    return df.to_dict(orient="records")