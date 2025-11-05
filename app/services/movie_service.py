from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database.models import Movie, Genre, Rating
from app.database.database import get_db

class MovieService:
    def __init__(self, db: Session):
        self.db = db
    
    def search_movies(self, title: Optional[str] = None, genres: Optional[List[str]] = None, 
                     year: Optional[int] = None, rating_min: Optional[float] = None, 
                     limit: int = 10) -> List[Dict]:
        """Search movies based on criteria"""
        query = self.db.query(Movie)
        
        # Filter by title (fuzzy search)
        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        
        # Filter by genres
        if genres:
            for genre in genres:
                query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))
        
        # Filter by year
        if year:
            query = query.filter(Movie.year == year)
        
        movies = query.limit(limit).all()
        
        # Convert to dict and add ratings
        result = []
        for movie in movies:
            movie_dict = self._movie_to_dict(movie)
            
            # Filter by rating if specified
            if rating_min and movie_dict.get('avg_rating', 0) < rating_min:
                continue
                
            result.append(movie_dict)
        
        return result
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Dict]:
        """Get movie details by ID"""
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
        return self._movie_to_dict(movie) if movie else None
    
    def get_recommendations(self, genres: Optional[List[str]] = None, 
                          year: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Get movie recommendations"""
        query = self.db.query(Movie)
        
        if genres:
            for genre in genres:
                query = query.join(Movie.genres).filter(Genre.name.ilike(f"%{genre}%"))
        
        if year:
            query = query.filter(Movie.year == year)
        
        # Order by average rating
        movies = query.limit(limit).all()
        result = [self._movie_to_dict(movie) for movie in movies]
        
        # Sort by rating
        return sorted(result, key=lambda x: x.get('avg_rating', 0), reverse=True)
    
    def _movie_to_dict(self, movie: Movie) -> Dict:
        """Convert Movie object to dictionary"""
        if not movie:
            return {}
        
        # Calculate average rating
        avg_rating = self.db.query(func.avg(Rating.rating)).filter(
            Rating.movie_id == movie.id
        ).scalar()
        
        return {
            'id': movie.id,
            'title': movie.title,
            'year': movie.year,
            'overview': movie.overview,
            'genres': [genre.name for genre in movie.genres],
            'avg_rating': float(avg_rating) if avg_rating else None,
            'cast': [{'actor': cast.actor_name, 'character': cast.character_name} 
                    for cast in movie.cast],
            'directors': [director.director_name for director in movie.directors]
        }