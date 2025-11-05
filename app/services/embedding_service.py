from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

class MovieEmbeddingService:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info("Initialized embedding model: all-MiniLM-L6-v2")
    
    def create_movie_content(self, movie_data):
        """Create rich content string for movie embedding"""
        content_parts = []
        
        if movie_data.get('title'):
            content_parts.append(f"Title: {movie_data['title']}")
        
        if movie_data.get('genres'):
            genres = movie_data['genres'] if isinstance(movie_data['genres'], list) else [movie_data['genres']]
            content_parts.append(f"Genres: {', '.join(genres)}")
        
        if movie_data.get('overview'):
            content_parts.append(f"Plot: {movie_data['overview']}")
        
        if movie_data.get('year'):
            content_parts.append(f"Year: {movie_data['year']}")
        
        if movie_data.get('cast'):
            cast_names = [actor.get('actor_name', actor.get('name', '')) for actor in movie_data['cast'][:5]]
            if cast_names:
                content_parts.append(f"Cast: {', '.join(cast_names)}")
        
        if movie_data.get('directors'):
            directors = movie_data['directors'] if isinstance(movie_data['directors'], list) else [movie_data['directors']]
            content_parts.append(f"Director: {', '.join(directors)}")
        
        return ". ".join(content_parts)
    
    def embed_documents(self, texts):
        """Embed multiple documents"""
        return self.model.embed_documents(texts)
    
    def embed_query(self, query):
        """Embed a single query"""
        return self.model.embed_query(query)