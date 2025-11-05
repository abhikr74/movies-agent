import re
from typing import Dict, List, Optional

class QueryProcessor:
    def __init__(self):
        self.genres = ['action', 'adventure', 'animation', 'children', 'comedy', 'crime', 
                      'documentary', 'drama', 'fantasy', 'horror', 'musical', 'mystery', 
                      'romance', 'sci-fi', 'thriller', 'war', 'western']
    
    def parse_query(self, query: str) -> Dict:
        """Parse natural language query and extract intent and parameters"""
        query_lower = query.lower()
        
        # Determine intent
        intent = self._detect_intent(query_lower)
        
        # Extract parameters
        params = {
            'genres': self._extract_genres(query_lower),
            'year': self._extract_year(query_lower),
            'title': self._extract_title(query_lower, intent),
            'rating_min': self._extract_rating(query_lower)
        }
        
        return {
            'intent': intent,
            'params': {k: v for k, v in params.items() if v is not None}
        }
    
    def _detect_intent(self, query: str) -> str:
        """Detect the intent of the query"""
        if any(word in query for word in ['recommend', 'suggest', 'find me', 'show me']):
            return 'recommendation'
        elif any(word in query for word in ['tell me about', 'what is', 'describe', 'info about']):
            return 'information'
        elif 'compare' in query:
            return 'comparison'
        else:
            return 'general'
    
    def _extract_genres(self, query: str) -> Optional[List[str]]:
        """Extract genres from query"""
        found_genres = []
        for genre in self.genres:
            if genre in query:
                found_genres.append(genre)
        return found_genres if found_genres else None
    
    def _extract_year(self, query: str) -> Optional[int]:
        """Extract year from query"""
        year_match = re.search(r'\b(19|20)\d{2}\b', query)
        return int(year_match.group()) if year_match else None
    
    def _extract_title(self, query: str, intent: str) -> Optional[str]:
        """Extract movie title from query"""
        if intent == 'information':
            # Look for patterns like "tell me about [title]"
            patterns = [
                r'tell me about (.+?)(?:\?|$)',
                r'what is (.+?)(?:\?|$)',
                r'describe (.+?)(?:\?|$)',
                r'info about (.+?)(?:\?|$)'
            ]
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    return match.group(1).strip()
        return None
    
    def _extract_rating(self, query: str) -> Optional[float]:
        """Extract minimum rating from query"""
        rating_match = re.search(r'rating.{0,10}(\d+(?:\.\d+)?)', query)
        return float(rating_match.group(1)) if rating_match else None