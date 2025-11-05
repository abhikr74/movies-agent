from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class MovieRAGService:
    def __init__(self, vector_store, llm_service, movie_service):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.movie_service = movie_service
    
    def process_query(self, query: str) -> Dict:
        """Complete RAG pipeline for movie queries"""
        logger.info(f"Processing RAG query: {query}")
        
        # 1. Determine search strategy based on query
        search_method = self._determine_search_method(query)
        
        # 2. Retrieve relevant movies
        if search_method == 'semantic':
            retrieved_docs = self.vector_store.similarity_search(query, k=10)
            movies_data = self._docs_to_movies(retrieved_docs)
        elif search_method == 'hybrid':
            retrieved_docs = self.vector_store.hybrid_search(query, k=10)
            movies_data = self._docs_to_movies(retrieved_docs)
        else:
            # Fallback to database search
            movies_data = self._fallback_database_search(query)
        
        # 3. Enhance with database information
        enhanced_movies = self._enhance_with_database(movies_data)
        
        # 4. Generate LLM response
        context = self._prepare_context(enhanced_movies, query)
        llm_response = self.llm_service.generate_response(query, context, 'rag')
        
        return {
            'response': llm_response,
            'movies': enhanced_movies[:5],
            'search_method': search_method,
            'total_found': len(enhanced_movies)
        }
    
    def _determine_search_method(self, query: str) -> str:
        """Determine best search method based on query characteristics"""
        query_lower = query.lower()
        
        # Semantic indicators
        semantic_indicators = ['like', 'similar', 'theme', 'plot', 'story', 'about']
        if any(indicator in query_lower for indicator in semantic_indicators):
            return 'semantic'
        
        # Hybrid indicators (mix of semantic and filters)
        hybrid_indicators = ['recommend', 'suggest', 'find', 'good']
        if any(indicator in query_lower for indicator in hybrid_indicators):
            return 'hybrid'
        
        return 'database'
    
    def _docs_to_movies(self, docs) -> List[Dict]:
        """Convert LangChain documents to movie data format"""
        movies = []
        for doc in docs:
            movie_data = {
                'id': doc.metadata.get('movie_id'),
                'title': doc.metadata.get('title'),
                'genres': doc.metadata.get('genres', []),
                'year': doc.metadata.get('year'),
                'avg_rating': doc.metadata.get('avg_rating'),
                'content': doc.page_content
            }
            movies.append(movie_data)
        return movies
    
    def _enhance_with_database(self, movies_data: List[Dict]) -> List[Dict]:
        """Enhance vector search results with full database information"""
        enhanced_movies = []
        
        for movie in movies_data:
            if movie.get('id'):
                # Get full movie details from database
                full_movie = self.movie_service.get_movie_by_id(movie['id'])
                if full_movie:
                    enhanced_movies.append(full_movie)
                else:
                    enhanced_movies.append(movie)
            else:
                enhanced_movies.append(movie)
        
        return enhanced_movies
    
    def _fallback_database_search(self, query: str) -> List[Dict]:
        """Fallback to traditional database search"""
        # Use existing query processor for database search
        from app.services.query_processor import QueryProcessor
        
        query_processor = QueryProcessor()
        parsed_query = query_processor.parse_query(query)
        
        return self.movie_service.search_movies(
            title=parsed_query['params'].get('title'),
            genres=parsed_query['params'].get('genres'),
            year=parsed_query['params'].get('year'),
            rating_min=parsed_query['params'].get('rating_min'),
            limit=10
        )
    
    def _prepare_context(self, movies: List[Dict], query: str) -> str:
        """Prepare context for LLM generation"""
        context_parts = [f"User Query: {query}\n"]
        context_parts.append("Relevant Movies:")
        
        for i, movie in enumerate(movies[:5], 1):
            movie_info = f"\n{i}. {movie['title']}"
            if movie.get('year'):
                movie_info += f" ({movie['year']})"
            if movie.get('genres'):
                movie_info += f" - Genres: {', '.join(movie['genres'])}"
            if movie.get('avg_rating'):
                movie_info += f" - Rating: {movie['avg_rating']:.1f}"
            if movie.get('overview'):
                movie_info += f" - Plot: {movie['overview'][:200]}..."
            
            context_parts.append(movie_info)
        
        return '\n'.join(context_parts)