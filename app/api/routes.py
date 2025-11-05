from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.schemas import ChatRequest, ChatResponse, MovieResponse, HealthResponse
from app.database.database import get_db
from app.services.query_processor import QueryProcessor
from app.services.movie_service import MovieService
from app.services.llm_service import LLMService

router = APIRouter()
query_processor = QueryProcessor()
llm_service = LLMService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint for conversational movie queries"""
    try:
        # Parse the query
        parsed_query = query_processor.parse_query(request.message)
        intent = parsed_query['intent']
        params = parsed_query['params']
        
        # Initialize RAG components
        from app.services.embedding_service import MovieEmbeddingService
        from app.services.vector_store import MovieVectorStore
        from app.services.rag_service import MovieRAGService
        
        movie_service = MovieService(db)
        
        # Try to load vector store, fallback to database search
        try:
            embedding_service = MovieEmbeddingService()
            vector_store = MovieVectorStore(embedding_service)
            
            if vector_store.load_index():
                # Use RAG pipeline
                rag_service = MovieRAGService(vector_store, llm_service, movie_service)
                rag_result = rag_service.process_query(request.message)
                
                return ChatResponse(
                    response=rag_result['response'],
                    movies=[MovieResponse(**movie) for movie in rag_result['movies']],
                    intent=intent,
                    params=params
                )
        except Exception as e:
            print(f"RAG pipeline error: {e}")
        
        # Fallback to traditional database search
        if intent == 'information' and 'title' in params:
            movies = movie_service.search_movies(title=params['title'], limit=1)
        elif intent == 'recommendation':
            movies = movie_service.get_recommendations(
                genres=params.get('genres'),
                year=params.get('year'),
                limit=10
            )
            if 'rating_min' in params:
                movies = [m for m in movies if m.get('avg_rating', 0) >= params['rating_min']]
        else:
            movies = movie_service.search_movies(
                title=params.get('title'),
                genres=params.get('genres'),
                year=params.get('year'),
                rating_min=params.get('rating_min'),
                limit=10
            )
        
        # Generate LLM response
        llm_response = llm_service.generate_response(request.message, movies, intent)
        
        # Convert movies to response format
        movie_responses = [MovieResponse(**movie) for movie in movies]
        
        return ChatResponse(
            response=llm_response,
            movies=movie_responses,
            intent=intent,
            params=params
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movies/search", response_model=List[MovieResponse])
async def search_movies(
    q: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    rating_min: Optional[float] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search movies with filters"""
    movie_service = MovieService(db)
    genres = [genre] if genre else None
    
    movies = movie_service.search_movies(
        title=q,
        genres=genres,
        year=year,
        rating_min=rating_min,
        limit=limit
    )
    
    return [MovieResponse(**movie) for movie in movies]

@router.get("/movies/semantic-search", response_model=List[MovieResponse])
async def semantic_search(
    query: str,
    k: int = 5,
    db: Session = Depends(get_db)
):
    """Semantic search endpoint using vector similarity"""
    try:
        from app.services.embedding_service import MovieEmbeddingService
        from app.services.vector_store import MovieVectorStore
        
        embedding_service = MovieEmbeddingService()
        vector_store = MovieVectorStore(embedding_service)
        
        if not vector_store.load_index():
            raise HTTPException(status_code=503, detail="Vector index not available")
        
        # Perform semantic search
        results = vector_store.similarity_search(query, k=k)
        
        # Convert to movie responses
        movie_service = MovieService(db)
        movies = []
        
        for doc in results:
            movie_id = doc.metadata.get('movie_id')
            if movie_id:
                movie = movie_service.get_movie_by_id(movie_id)
                if movie:
                    movies.append(movie)
        
        return [MovieResponse(**movie) for movie in movies]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get movie details by ID"""
    movie_service = MovieService(db)
    movie = movie_service.get_movie_by_id(movie_id)
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return MovieResponse(**movie)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="Movie AI Agent is running")

@router.post("/admin/build-index")
async def build_vector_index(db: Session = Depends(get_db)):
    """Build FAISS vector index from movie database"""
    try:
        from app.services.embedding_service import MovieEmbeddingService
        from app.services.vector_store import MovieVectorStore
        
        movie_service = MovieService(db)
        
        # Get all movies for indexing
        all_movies = movie_service.search_movies(limit=10000)  # Get all movies
        
        if not all_movies:
            raise HTTPException(status_code=404, detail="No movies found in database")
        
        # Build vector index
        embedding_service = MovieEmbeddingService()
        vector_store = MovieVectorStore(embedding_service)
        vector_store.build_index(all_movies)
        vector_store.save_index()
        
        return {
            "message": f"Vector index built successfully for {len(all_movies)} movies",
            "index_path": "data/processed/movie_faiss_index"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))