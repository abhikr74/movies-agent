import requests
import json
from typing import List, Dict
from app.config import OLLAMA_BASE_URL

class LLMService:
    def __init__(self):
        self.ollama_url = OLLAMA_BASE_URL
        self.model = "llama3.1:8b"  # More capable model
    
    def generate_response(self, query: str, context_data, intent: str) -> str:
        """Generate conversational response using LLM"""
        try:
            return self._generate_with_ollama(query, context_data, intent)
        except Exception as e:
            print(f"Ollama error: {e}")
            return self._generate_fallback_response(query, context_data, intent)
    
    def _generate_with_ollama(self, query: str, context_data, intent: str) -> str:
        """Generate response using Ollama"""
        if isinstance(context_data, str):
            context = context_data
        else:
            context = self._prepare_context(context_data)
        
        prompt = f"""You are a helpful movie recommendation assistant. Based on the user's query and the movie data provided, give a conversational and informative response.

User Query: {query}
Intent: {intent}

Movie Data:
{context}

Provide a natural, conversational response that directly addresses the user's question. Keep it concise but informative."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def _generate_fallback_response(self, query: str, context_data, intent: str) -> str:
        """Generate fallback response when LLM is unavailable"""
        movies_data = context_data if isinstance(context_data, list) else []
        
        if intent == 'recommendation' or intent == 'rag':
            if movies_data:
                titles = [movie['title'] for movie in movies_data[:5]]
                return f"Based on your request, I recommend these movies: {', '.join(titles)}. These movies match your criteria and have good ratings."
            else:
                return "I couldn't find any movies matching your criteria. Try adjusting your search parameters."
        
        elif intent == 'information':
            if movies_data:
                movie = movies_data[0]
                return f"{movie['title']} ({movie.get('year', 'Unknown year')}) is a {', '.join(movie.get('genres', []))} movie with an average rating of {movie.get('avg_rating', 'N/A')}."
            else:
                return "I couldn't find information about that movie."
        
        else:
            return "I found some movies that might interest you. Let me know if you'd like more specific recommendations!"
    
    def _prepare_context(self, movies_data: List[Dict]) -> str:
        """Prepare movie data context for LLM"""
        if not movies_data:
            return "No movies found."
        
        context_parts = []
        for movie in movies_data[:5]:  # Limit to top 5 movies
            movie_info = f"- {movie['title']}"
            if movie.get('year'):
                movie_info += f" ({movie['year']})"
            if movie.get('genres'):
                movie_info += f" - Genres: {', '.join(movie['genres'])}"
            if movie.get('avg_rating'):
                movie_info += f" - Rating: {movie['avg_rating']:.1f}"
            context_parts.append(movie_info)
        
        return "\n".join(context_parts)