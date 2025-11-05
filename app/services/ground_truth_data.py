# Ground truth dataset for movie evaluation
# Based on 5 well-known movies with 3 variables each (15 total observations)

GROUND_TRUTH_DATASET = [
    # Movie Title Extraction Focus (5 observations)
    {
        "observation_id": 1,
        "query": "Tell me about the movie Inception",
        "focus_variable": "movie_title",
        "movie_title": "Inception",
        "avg_rating": 4.07,
        "release_year": 2010,
        "source_context": "Inception (2010) is a sci-fi thriller directed by Christopher Nolan with rating 4.07/5"
    },
    {
        "observation_id": 2,
        "query": "What do you know about Toy Story?",
        "focus_variable": "movie_title",
        "movie_title": "Toy Story",
        "avg_rating": 3.92,
        "release_year": 1995,
        "source_context": "Toy Story (1995) is an animated film with rating 3.92/5 starring Tom Hanks"
    },
    {
        "observation_id": 3,
        "query": "Give me info on The Matrix",
        "focus_variable": "movie_title",
        "movie_title": "The Matrix",
        "avg_rating": 4.32,
        "release_year": 1999,
        "source_context": "The Matrix (1999) is an action sci-fi film with rating 4.32/5 starring Keanu Reeves"
    },
    {
        "observation_id": 4,
        "query": "Describe the film Titanic",
        "focus_variable": "movie_title",
        "movie_title": "Titanic",
        "avg_rating": 3.89,
        "release_year": 1997,
        "source_context": "Titanic (1997) is a romance drama film with rating 3.89/5 starring Leonardo DiCaprio"
    },
    {
        "observation_id": 5,
        "query": "What about The Lion King movie?",
        "focus_variable": "movie_title",
        "movie_title": "The Lion King",
        "avg_rating": 4.15,
        "release_year": 1994,
        "source_context": "The Lion King (1994) is an animated film with rating 4.15/5 from Disney"
    },
    
    # Average Rating Extraction Focus (5 observations)
    {
        "observation_id": 6,
        "query": "What is the rating of Inception?",
        "focus_variable": "avg_rating",
        "movie_title": "Inception",
        "avg_rating": 4.07,
        "release_year": 2010,
        "source_context": "Inception has an average rating of 4.07 out of 5 stars from users"
    },
    {
        "observation_id": 7,
        "query": "How good is Toy Story rated?",
        "focus_variable": "avg_rating",
        "movie_title": "Toy Story",
        "avg_rating": 3.92,
        "release_year": 1995,
        "source_context": "Toy Story is rated 3.92/5 by moviegoers and critics"
    },
    {
        "observation_id": 8,
        "query": "What's the score for The Matrix?",
        "focus_variable": "avg_rating",
        "movie_title": "The Matrix",
        "avg_rating": 4.32,
        "release_year": 1999,
        "source_context": "The Matrix has a high rating of 4.32 out of 5 stars"
    },
    {
        "observation_id": 9,
        "query": "How is Titanic rated by users?",
        "focus_variable": "avg_rating",
        "movie_title": "Titanic",
        "avg_rating": 3.89,
        "release_year": 1997,
        "source_context": "Titanic received an average user rating of 3.89/5"
    },
    {
        "observation_id": 10,
        "query": "What rating does The Lion King have?",
        "focus_variable": "avg_rating",
        "movie_title": "The Lion King",
        "avg_rating": 4.15,
        "release_year": 1994,
        "source_context": "The Lion King has an excellent rating of 4.15 out of 5"
    },
    
    # Release Year Extraction Focus (5 observations)
    {
        "observation_id": 11,
        "query": "When was Inception released?",
        "focus_variable": "release_year",
        "movie_title": "Inception",
        "avg_rating": 4.07,
        "release_year": 2010,
        "source_context": "Inception was released in 2010 and became a blockbuster hit"
    },
    {
        "observation_id": 12,
        "query": "What year did Toy Story come out?",
        "focus_variable": "release_year",
        "movie_title": "Toy Story",
        "avg_rating": 3.92,
        "release_year": 1995,
        "source_context": "Toy Story came out in 1995 as Pixar's first feature film"
    },
    {
        "observation_id": 13,
        "query": "When was The Matrix made?",
        "focus_variable": "release_year",
        "movie_title": "The Matrix",
        "avg_rating": 4.32,
        "release_year": 1999,
        "source_context": "The Matrix was made and released in 1999 by the Wachowski sisters"
    },
    {
        "observation_id": 14,
        "query": "What year was Titanic released?",
        "focus_variable": "release_year",
        "movie_title": "Titanic",
        "avg_rating": 3.89,
        "release_year": 1997,
        "source_context": "Titanic was released in 1997 and won multiple Academy Awards"
    },
    {
        "observation_id": 15,
        "query": "When did The Lion King premiere?",
        "focus_variable": "release_year",
        "movie_title": "The Lion King",
        "avg_rating": 4.15,
        "release_year": 1994,
        "source_context": "The Lion King premiered in 1994 and became Disney's highest-grossing animated film"
    }
]

# Variable definitions for evaluation
EVALUATION_VARIABLES = {
    "movie_title": {
        "type": "categorical",
        "description": "Movie name/title extraction",
        "evaluation_method": "fuzzy_match_and_similarity"
    },
    "avg_rating": {
        "type": "numeric", 
        "description": "Average user rating (1-5 scale)",
        "evaluation_method": "tolerance_based_accuracy",
        "tolerance": 0.05  # ±5%
    },
    "release_year": {
        "type": "numeric",
        "description": "Year movie was released", 
        "evaluation_method": "exact_match"
    }
}

def get_ground_truth_by_id(observation_id: int):
    """Get ground truth data by observation ID"""
    for obs in GROUND_TRUTH_DATASET:
        if obs["observation_id"] == observation_id:
            return obs
    return None

def get_ground_truth_by_movie(movie_title: str):
    """Get all ground truth data for a specific movie"""
    return [obs for obs in GROUND_TRUTH_DATASET if obs["movie_title"].lower() == movie_title.lower()]

def get_test_queries():
    """Get all test queries for evaluation"""
    return [{"id": obs["observation_id"], "query": obs["query"], "focus": obs["focus_variable"]} 
            for obs in GROUND_TRUTH_DATASET]