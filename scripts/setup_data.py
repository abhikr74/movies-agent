#!/usr/bin/env python3
"""
Data setup script for Movie AI Agent
Downloads and loads MovieLens dataset into SQLite database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_ingestion import DataIngestionService
from app.database.database import create_tables

def main():
    print("Setting up Movie AI Agent database...")
    
    # Create database tables
    print("Creating database tables...")
    create_tables()
    
    # Load data
    print("Loading MovieLens data...")
    ingestion_service = DataIngestionService()
    ingestion_service.load_data_to_db()
    
    # Build vector index
    print("Building vector index...")
    try:
        from app.services.embedding_service import MovieEmbeddingService
        from app.services.vector_store import MovieVectorStore
        from app.services.movie_service import MovieService
        from app.database.database import SessionLocal
        
        db = SessionLocal()
        movie_service = MovieService(db)
        all_movies = movie_service.search_movies(limit=10000)
        
        if all_movies:
            embedding_service = MovieEmbeddingService()
            vector_store = MovieVectorStore(embedding_service)
            vector_store.build_index(all_movies)
            vector_store.save_index()
            print(f"Vector index built for {len(all_movies)} movies")
        
        db.close()
    except Exception as e:
        print(f"Vector index build failed: {e}")
    
    print("Setup complete!")

if __name__ == "__main__":
    main()