from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_db():
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    database_name = os.getenv("DATABASE_NAME", "rag_csv_db")
    client = MongoClient(mongodb_uri)
    return client[database_name]

def store_file_metadata(file_id: str, file_name: str, content: list):
    try:
        db = get_db()
        collection = db["csv_files"]
        result = collection.insert_one({
            "file_id": file_id,
            "file_name": file_name,
            "document": content  # Store CSV rows as a list of dictionaries
        })
        logger.info(f"Stored file with ID: {file_id}")
        return result
    except Exception as e:
        logger.error(f"Error storing file {file_id}: {str(e)}")
        raise

def get_file(file_id: str):
    try:
        db = get_db()
        collection = db["csv_files"]
        result = collection.find_one({"file_id": file_id})
        if result:
            logger.info(f"Found file with ID: {file_id}")
            return result
        logger.warning(f"No file found with ID: {file_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving file {file_id}: {str(e)}")
        return None

def delete_file(file_id: str):
    db = get_db()
    collection = db["csv_files"]
    return collection.delete_one({"file_id": file_id})

def get_all_files():
    db = get_db()
    collection = db["csv_files"]
    return list(collection.find({}, {"_id": 0, "file_id": 1, "file_name": 1}))