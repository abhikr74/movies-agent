import re
from typing import Dict, List, Optional, Any
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class MovieEvaluationService:
    """Evaluation service for movie information extraction"""
    
    def __init__(self, tolerance=0.05):
        self.tolerance = tolerance
    
    def evaluate_movie_title_extraction(self, predicted: str, actual: str) -> Dict:
        """Evaluate movie title extraction (categorical variable)"""
        if not predicted or not actual:
            return {'exact_match': False, 'similarity_score': 0.0, 'token_overlap': 0.0, 'fuzzy_match': False}
        
        predicted_clean = predicted.lower().strip()
        actual_clean = actual.lower().strip()
        
        # Exact match
        exact_match = predicted_clean == actual_clean
        
        # Similarity score using SequenceMatcher
        similarity = SequenceMatcher(None, predicted_clean, actual_clean).ratio()
        
        # Token overlap (handles "The Matrix" vs "Matrix")
        pred_tokens = set(predicted_clean.split())
        actual_tokens = set(actual_clean.split())
        
        if actual_tokens:
            token_overlap = len(pred_tokens.intersection(actual_tokens)) / len(actual_tokens)
        else:
            token_overlap = 0.0
        
        # Fuzzy match threshold
        fuzzy_match = similarity >= 0.8
        
        return {
            'exact_match': exact_match,
            'similarity_score': similarity,
            'token_overlap': token_overlap,
            'fuzzy_match': fuzzy_match
        }
    
    def evaluate_numeric_extraction(self, predicted: Any, actual: float, variable_type: str) -> Dict:
        """Evaluate numeric variables (rating, year) with tolerance"""
        try:
            # Extract numeric value from predicted response
            if isinstance(predicted, str):
                pred_num = self._extract_numeric_from_text(predicted, variable_type)
            else:
                pred_num = float(predicted)
            
            if pred_num is None:
                return {
                    'exact_match': False,
                    'tolerance_match': False,
                    'error_rate': 1.0,
                    'predicted_value': None,
                    'actual_value': actual,
                    'extraction_failed': True
                }
            
            actual_num = float(actual)
            
            # Exact match
            exact_match = pred_num == actual_num
            
            # Tolerance match (±5% for ratings, exact for years)
            if variable_type == 'avg_rating':
                error_rate = abs(pred_num - actual_num) / actual_num if actual_num != 0 else 1.0
                tolerance_match = error_rate <= self.tolerance
            else:  # release_year
                tolerance_match = exact_match  # Years should be exact
                error_rate = 0.0 if exact_match else 1.0
            
            return {
                'exact_match': exact_match,
                'tolerance_match': tolerance_match,
                'error_rate': error_rate,
                'predicted_value': pred_num,
                'actual_value': actual_num,
                'extraction_failed': False
            }
            
        except Exception as e:
            logger.error(f"Error in numeric evaluation: {e}")
            return {
                'exact_match': False,
                'tolerance_match': False,
                'error_rate': 1.0,
                'predicted_value': None,
                'actual_value': actual,
                'extraction_failed': True
            }
    
    def _extract_numeric_from_text(self, text: str, variable_type: str) -> Optional[float]:
        """Rule-based extraction of numeric values from text"""
        text_lower = text.lower()
        
        if variable_type == 'avg_rating':
            # Look for rating patterns: "4.2", "rating of 3.8", "rated 4.5/5"
            patterns = [
                r'rating.*?(\d+\.?\d*)',
                r'rated.*?(\d+\.?\d*)',
                r'score.*?(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*(?:/5|out of 5|stars?)',
                r'(\d+\.?\d*)'  # Any decimal number as fallback
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    value = float(match.group(1))
                    # Validate rating range (0-5)
                    if 0 <= value <= 5:
                        return value
        
        elif variable_type == 'release_year':
            # Look for year patterns: "1999", "released in 2010", "came out in 1995"
            patterns = [
                r'(?:released|made|came out).*?(\d{4})',
                r'(\d{4})',  # Any 4-digit year
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    year = int(match.group(1))
                    # Validate year range (1900-2030)
                    if 1900 <= year <= 2030:
                        return float(year)
        
        return None
    
    def evaluate_groundedness(self, response: str, source_chunks: List[Dict]) -> float:
        """Evaluate how grounded the response is in source documents"""
        if not response or not source_chunks:
            return 0.0
        
        response_lower = response.lower()
        grounded_facts = 0
        
        for chunk in source_chunks:
            chunk_text = chunk.get('text', '') or chunk.get('title', '')
            if not chunk_text:
                continue
                
            chunk_lower = chunk_text.lower()
            # Check if key terms from chunk appear in response
            chunk_terms = [term for term in chunk_lower.split() if len(term) > 3][:10]
            
            if any(term in response_lower for term in chunk_terms):
                grounded_facts += 1
        
        return grounded_facts / len(source_chunks) if source_chunks else 0.0
    
    def evaluate_truthfulness(self, predicted_values: Dict, ground_truth: Dict) -> float:
        """Overall factual accuracy across all variables"""
        if not ground_truth:
            return 0.0
        
        correct_facts = 0
        total_facts = len(ground_truth)
        
        for key, true_value in ground_truth.items():
            if key not in predicted_values:
                continue
                
            predicted_value = predicted_values[key]
            
            if key == 'movie_title':
                # Use fuzzy match for movie titles
                result = self.evaluate_movie_title_extraction(predicted_value, true_value)
                if result['fuzzy_match']:
                    correct_facts += 1
            elif key in ['avg_rating', 'release_year']:
                # Use tolerance match for numeric values
                result = self.evaluate_numeric_extraction(predicted_value, true_value, key)
                if result['tolerance_match']:
                    correct_facts += 1
        
        return correct_facts / total_facts