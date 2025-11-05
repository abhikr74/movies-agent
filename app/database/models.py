from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

movie_genre = Table('movie_genre', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer)
    overview = Column(String)
    imdb_id = Column(String)
    
    genres = relationship("Genre", secondary=movie_genre, back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
    cast = relationship("Cast", back_populates="movie")
    directors = relationship("Director", back_populates="movie")

class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    movies = relationship("Movie", secondary=movie_genre, back_populates="genres")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    rating = Column(Float)
    
    movie = relationship("Movie", back_populates="ratings")

class Cast(Base):
    __tablename__ = "cast"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    actor_name = Column(String)
    character_name = Column(String)
    
    movie = relationship("Movie", back_populates="cast")

class Director(Base):
    __tablename__ = "directors"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    director_name = Column(String)
    
    movie = relationship("Movie", back_populates="directors")