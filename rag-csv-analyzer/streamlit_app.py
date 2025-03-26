import streamlit as st
import requests
import pandas as pd
import os
import io

# Update BASE_URL for Heroku
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.title("RAG CSV Analyzer")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    try:
        # Try to read CSV with different settings
        try:
            df = pd.read_csv(uploaded_file)
        except pd.errors.ParserError:
            # Try with different separator
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        
        # Show preview
        st.write("Preview of your CSV:")
        st.dataframe(df.head())
        st.write(f"Total rows: {len(df)}, Total columns: {len(df.columns)}")
        st.write("Columns:", ", ".join(df.columns.tolist()))
        
        if st.button("Confirm Upload"):
            # Convert DataFrame back to CSV for upload
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            files = {"file": ("uploaded.csv", csv_buffer.getvalue(), "text/csv")}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                file_id = response.json()["file_id"]
                st.success(f"File uploaded successfully!")
                st.info(f"Your File ID: {file_id}")
                # Store file_id in session state
                st.session_state['last_file_id'] = file_id
                # Auto-populate the query section
                st.session_state['query_file_id'] = file_id
            else:
                st.error(response.json()["detail"])
    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")
        st.write("Please ensure your CSV file is properly formatted and try again.")

# List Files
if st.button("List Files"):
    response = requests.get(f"{BASE_URL}/files")
    if response.status_code == 200:
        files = response.json()["files"]
        st.write("Available Files:")
        for file in files:
            st.write(f"ID: {file['file_id']} - Name: {file['file_name']}")
    else:
        st.error("Error fetching files")

# Query with streaming
st.subheader("Query CSV")
file_id = st.text_input("File ID", value=st.session_state.get('query_file_id', ''))
query = st.text_area("Enter your query")
if st.button("Submit Query"):
    if not file_id or not query:
        st.error("Please provide both File ID and Query")
    else:
        with st.spinner("Processing query..."):
            response = requests.post(f"{BASE_URL}/query", json={"file_id": file_id, "query": query})
            if response.status_code == 200:
                st.success("Response:")
                st.write(response.json()["response"])
            else:
                st.error(response.json()["detail"])