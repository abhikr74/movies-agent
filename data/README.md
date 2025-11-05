# Data Directory

This directory contains the movie dataset and processed files.

## Structure

- `raw/` - Original MovieLens dataset files (downloaded during setup)
- `processed/` - Processed database and index files (generated during setup)

## Setup

Run the setup script to populate this directory:

```bash
python scripts/setup_data.py
```

This will:
1. Download the MovieLens dataset
2. Create the SQLite database
3. Build the FAISS vector index
4. Generate embeddings for semantic search