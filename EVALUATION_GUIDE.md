# Movie RAG Evaluation Pipeline - Testing Guide

## Overview
This evaluation pipeline tests the movie RAG system's ability to extract specific information from movie queries using:
- **2 Numeric Variables**: Average Rating, Release Year
- **1 Categorical Variable**: Movie Title
- **15 Ground Truth Observations** (5 per variable)
- **Rule-Based Extraction** for reliable metric calculation

## Quick Start

### 1. Ensure System is Running
```bash
# Activate environment
conda activate movies-agent

# Start the movie agent server (in one terminal)
python scripts/run_server.py

# Verify health
curl http://localhost:8000/api/v1/health
```

### 2. Run Complete Evaluation
```bash
# Run full evaluation pipeline (in another terminal)
python scripts/run_evaluation.py
```

### 3. Expected Output
```
Starting Movie RAG Evaluation Pipeline
==================================================
Initializing evaluation pipeline...
Running evaluation on 15 ground truth observations...

============================================================
MOVIE EVALUATION PIPELINE RESULTS
============================================================
Total Observations: 15
Successful Evaluations: 15
Success Rate: 100.0%
Average Groundedness: 0.85
Average Truthfulness: 0.73

VARIABLE-SPECIFIC METRICS:
----------------------------------------

MOVIE_TITLE:
  Tests: 5
  Exact Accuracy: 80.0%
  Fuzzy Match Accuracy: 100.0%
  Avg Similarity: 0.92

AVG_RATING:
  Tests: 5
  Exact Accuracy: 60.0%
  Tolerance Accuracy: 100.0%
  Avg Error Rate: 2.1%

RELEASE_YEAR:
  Tests: 5
  Exact Accuracy: 100.0%
  Tolerance Accuracy: 100.0%
  Avg Error Rate: 0.0%
```

## Test Cases Overview

### Ground Truth Movies (5 total)
1. **Inception** (2010) - Rating: 4.07 - Sci-Fi
2. **Toy Story** (1995) - Rating: 3.92 - Animation  
3. **The Matrix** (1999) - Rating: 4.32 - Action
4. **Titanic** (1997) - Rating: 3.89 - Romance
5. **The Lion King** (1994) - Rating: 4.15 - Animation

### Test Queries (15 total)

#### Movie Title Extraction (5 queries)
```
"Tell me about the movie Inception"
"What do you know about Toy Story?"
"Give me info on The Matrix"
"Describe the film Titanic"
"What about The Lion King movie?"
```

#### Rating Extraction (5 queries)
```
"What is the rating of Inception?"
"How good is Toy Story rated?"
"What's the score for The Matrix?"
"How is Titanic rated by users?"
"What rating does The Lion King have?"
```

#### Year Extraction (5 queries)
```
"When was Inception released?"
"What year did Toy Story come out?"
"When was The Matrix made?"
"What year was Titanic released?"
"When did The Lion King premiere?"
```

## Evaluation Metrics Explained

### 1. Numeric Variables (Rating, Year)
- **Exact Match**: Predicted value exactly equals ground truth
- **Tolerance Match**: Within ±5% for ratings, exact for years
- **Error Rate**: |predicted - actual| / actual

### 2. Categorical Variables (Movie Title)
- **Exact Match**: Exact string match (case-insensitive)
- **Fuzzy Match**: ≥80% similarity using SequenceMatcher
- **Token Overlap**: Handles "The Matrix" vs "Matrix"

### 3. RAG-Specific Metrics
- **Groundedness**: How well response is grounded in retrieved documents
- **Truthfulness**: Overall factual accuracy across all variables

## Rule-Based Extraction Patterns

### Rating Extraction
```python
patterns = [
    r'rating.*?(\d+\.?\d*)',           # "rating of 4.2"
    r'rated.*?(\d+\.?\d*)',            # "rated 3.8"
    r'(\d+\.?\d*)\s*(?:/5|out of 5)',  # "4.2/5" or "4.2 out of 5"
    r'(\d+\.?\d*)'                     # Any decimal as fallback
]
```

### Year Extraction
```python
patterns = [
    r'(?:released|made|came out).*?(\d{4})',  # "released in 2010"
    r'(\d{4})'                                # Any 4-digit year
]
```

## Manual Testing

### Test Individual Queries
```bash
# Test movie title extraction
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about the movie Inception"}'

# Test rating extraction  
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the rating of Inception?"}'

# Test year extraction
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "When was Inception released?"}'
```

### Analyze Responses
Look for:
- **Movie Title**: Should mention "Inception" clearly
- **Rating**: Should include "4.07" or similar numeric value
- **Year**: Should mention "2010"

## Troubleshooting

### Common Issues

1. **RAG Pipeline Not Available**
   ```
   Warning: RAG index not available, using fallback
   ```
   **Solution**: Run `python scripts/setup_data.py` to build vector index

2. **Low Groundedness Scores**
   ```
   Average Groundedness: 0.20
   ```
   **Solution**: Check if vector index is properly loaded and movies exist in database

3. **Extraction Failures**
   ```
   extraction_failed: True
   ```
   **Solution**: Check if LLM responses contain the expected information

### Debug Individual Observations
```python
# In Python console
from app.services.evaluation_pipeline import MovieEvaluationPipeline
from app.database.database import SessionLocal

db = SessionLocal()
pipeline = MovieEvaluationPipeline(db)

# Test single observation
obs = pipeline.GROUND_TRUTH_DATASET[0]  # First observation
result = pipeline._evaluate_single_observation(obs)
print(result)
```

## Expected Performance Benchmarks

### Good Performance
- **Success Rate**: >90%
- **Exact Accuracy**: >70% for all variables
- **Tolerance Accuracy**: >90% for numeric variables
- **Groundedness**: >0.8
- **Truthfulness**: >0.7

### Excellent Performance  
- **Success Rate**: 100%
- **Exact Accuracy**: >90% for all variables
- **Tolerance Accuracy**: 100% for numeric variables
- **Groundedness**: >0.9
- **Truthfulness**: >0.9

## Files Generated

After running evaluation:
- `data/processed/evaluation_results.json` - Detailed results
- Console output with summary metrics
- Logs in terminal showing progress

## Technical Design Decisions

1. **Rule-based extraction approach**
   - Deterministic and reliable results
   - Faster evaluation compared to LLM-based extraction
   - Easier to debug and maintain

2. **Fuzzy matching for movie titles**
   - SequenceMatcher for similarity scoring
   - Token overlap for partial matches
   - 80% similarity threshold for flexibility

3. **Tolerance-based accuracy metrics**
   - Accounts for rounding differences in ratings
   - More realistic evaluation for numeric values
   - 5% tolerance for ratings, exact match for years

4. **Future improvements**
   - Expand dataset with more movies and variables
   - Implement cross-validation techniques
   - Add semantic similarity metrics
   - Include comprehensive error analysis