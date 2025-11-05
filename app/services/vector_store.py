from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os
import logging

logger = logging.getLogger(__name__)

class MovieVectorStore:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.vector_store = None
    
    def build_index(self, movies_data):
        """Build FAISS index from movie data"""
        logger.info(f"Building FAISS index for {len(movies_data)} movies")
        
        documents = []
        for movie in movies_data:
            content = self.embedding_service.create_movie_content(movie)
            
            doc = Document(
                page_content=content,
                metadata={
                    'movie_id': movie.get('id'),
                    'title': movie.get('title'),
                    'genres': movie.get('genres', []),
                    'year': movie.get('year'),
                    'avg_rating': movie.get('avg_rating')
                }
            )
            documents.append(doc)
        
        self.vector_store = FAISS.from_documents(
            documents, 
            self.embedding_service.model
        )
        logger.info("FAISS index built successfully")
    
    def save_index(self, path="data/processed/movie_faiss_index"):
        """Save FAISS index to disk"""
        if self.vector_store:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.vector_store.save_local(path)
            logger.info(f"FAISS index saved to {path}")
    
    def load_index(self, path="data/processed/movie_faiss_index"):
        """Load FAISS index from disk"""
        if os.path.exists(path):
            self.vector_store = FAISS.load_local(
                path, 
                self.embedding_service.model,
                allow_dangerous_deserialization=True
            )
            logger.info(f"FAISS index loaded from {path}")
            return True
        return False
    
    def similarity_search(self, query, k=5):
        """Semantic search for movies"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_scores(self, query, k=5):
        """Semantic search with similarity scores"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def hybrid_search(self, query, k=5, alpha=0.7):
        """Hybrid semantic + keyword search"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        # Get semantic results with scores
        semantic_results = self.vector_store.similarity_search_with_score(query, k=k*2)
        
        hybrid_results = []
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        for doc, sem_score in semantic_results:
            text_lower = doc.page_content.lower()
            
            # Keyword scoring
            kw_score = 0
            
            # Exact phrase match bonus
            if query_lower in text_lower:
                kw_score += 10
            
            # Individual term frequency
            for term in query_terms:
                kw_score += text_lower.count(term) * 2
            
            # Movie-specific term bonuses
            movie_terms = ['action', 'comedy', 'drama', 'thriller', 'romance', 'sci-fi']
            for term in movie_terms:
                if term in query_lower and term in text_lower:
                    kw_score += 3
            
            # Year bonus
            if any(year in query_lower and year in text_lower for year in ['2020', '2019', '2018', '2017']):
                kw_score += 5
            
            # Normalize keyword score
            kw_score_norm = min(kw_score / 20.0, 1.0)
            
            # Combine scores (lower semantic score is better, so invert it)
            semantic_score_norm = 1.0 / (1.0 + sem_score)
            hybrid_score = alpha * semantic_score_norm + (1 - alpha) * kw_score_norm
            
            hybrid_results.append((doc, hybrid_score))
        
        # Sort by hybrid score (higher is better)
        hybrid_results.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in hybrid_results[:k]]