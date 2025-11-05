import pandas as pd
import requests
import zipfile
import os
from sqlalchemy.orm import Session
from app.database.models import Movie, Genre, Rating, Cast, Director
from app.database.database import SessionLocal

class DataIngestionService:
    def __init__(self):
        self.data_dir = "data/raw"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def download_movielens_data(self):
        """Download MovieLens small dataset"""
        url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
        zip_path = f"{self.data_dir}/ml-latest-small.zip"
        
        if not os.path.exists(zip_path):
            response = requests.get(url)
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
    
    def load_data_to_db(self):
        """Load MovieLens data into database"""
        self.download_movielens_data()
        
        db = SessionLocal()
        try:
            # Load movies
            movies_df = pd.read_csv(f"{self.data_dir}/ml-latest-small/movies.csv")
            ratings_df = pd.read_csv(f"{self.data_dir}/ml-latest-small/ratings.csv")
            
            # Process genres
            all_genres = set()
            for genres_str in movies_df['genres'].dropna():
                all_genres.update(genres_str.split('|'))
            
            for genre_name in all_genres:
                if genre_name != "(no genres listed)":
                    genre = db.query(Genre).filter(Genre.name == genre_name).first()
                    if not genre:
                        db.add(Genre(name=genre_name))
            db.commit()
            
            # Process movies
            for _, row in movies_df.iterrows():
                movie = db.query(Movie).filter(Movie.id == row['movieId']).first()
                if not movie:
                    title_year = row['title'].rsplit(' (', 1)
                    title = title_year[0]
                    year = int(title_year[1][:-1]) if len(title_year) > 1 and title_year[1][:-1].isdigit() else None
                    
                    movie = Movie(
                        id=row['movieId'],
                        title=title,
                        year=year,
                        overview=""
                    )
                    db.add(movie)
                    
                    # Add genres
                    if pd.notna(row['genres']):
                        for genre_name in row['genres'].split('|'):
                            if genre_name != "(no genres listed)":
                                genre = db.query(Genre).filter(Genre.name == genre_name).first()
                                if genre:
                                    movie.genres.append(genre)
            
            db.commit()
            
            # Process ratings
            for _, row in ratings_df.iterrows():
                rating = Rating(
                    movie_id=row['movieId'],
                    rating=row['rating']
                )
                db.add(rating)
            
            db.commit()
            print("Data loaded successfully!")
            
        finally:
            db.close()