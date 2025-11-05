import streamlit as st
import requests
import json
import os
from typing import Dict, List

# Configuration - support environment variable for Docker deployments
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def chat_with_agent(message: str) -> Dict:
    """Send message to chat endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message},
            timeout=90
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        return {"error": str(e)}

def get_semantic_search_chunks(query: str, k: int = 5) -> List[Dict]:
    """Get semantic search chunks to show RAG retrieval"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/movies/semantic-search",
            params={"query": query, "k": k},
            timeout=30
        )
        return response.json() if response.status_code == 200 else []
    except:
        return []

def load_ground_truth_data() -> List[Dict]:
    """Load ground truth data for comparison"""
    try:
        # Try to load from the evaluation service
        import sys
        sys.path.append('.')
        from app.services.ground_truth_data import GROUND_TRUTH_DATA
        return GROUND_TRUTH_DATA
    except:
        return []

def extract_movie_info(text: str) -> Dict:
    """Extract movie information using rule-based patterns"""
    import re
    from difflib import SequenceMatcher
    
    # Extract movie titles (look for quoted titles or capitalized words)
    title_patterns = [
        r'"([^"]+)"',
        r"'([^']+)'",
        r'\b([A-Z][a-zA-Z\s]+(?:(?:[A-Z][a-zA-Z\s]*)|(?:\d+)))\b'
    ]
    
    titles = []
    for pattern in title_patterns:
        matches = re.findall(pattern, text)
        titles.extend(matches)
    
    # Extract ratings (decimal numbers)
    rating_pattern = r'\b(\d+\.\d+)\b'
    ratings = [float(match) for match in re.findall(rating_pattern, text)]
    
    # Extract years (4-digit numbers starting with 19 or 20)
    year_pattern = r'\b(19|20)\d{2}\b'
    years = [int(match) for match in re.findall(year_pattern, text)]
    
    return {
        'titles': titles[:3],  # Top 3 titles
        'ratings': ratings[:3],  # Top 3 ratings
        'years': years[:3]  # Top 3 years
    }

def search_movies(query: str, limit: int = 5) -> List[Dict]:
    """Search movies using the search endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/movies/search",
            params={"q": query, "limit": limit},
            timeout=30
        )
        return response.json() if response.status_code == 200 else []
    except:
        return []

def display_movie_card(movie: Dict, show_chunk_info: bool = False):
    """Display a movie card"""
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.write(f"**{movie['title']}**")
            if movie.get('year'):
                st.write(f"📅 {movie['year']}")
            if movie.get('avg_rating'):
                st.write(f"⭐ {movie['avg_rating']:.1f}")
        
        with col2:
            if movie.get('genres'):
                st.write(f"🎭 {', '.join(movie['genres'])}")
            if movie.get('overview'):
                st.write(f"📖 {movie['overview'][:200]}...")
            
            if show_chunk_info:
                st.caption(f"Movie ID: {movie.get('id', 'N/A')}")

def display_rag_analysis(query: str, response: str):
    """Display RAG analysis including chunks and ground truth comparison"""
    st.subheader("🔍 RAG Analysis")
    
    # Show retrieved chunks
    with st.expander("📚 Retrieved Chunks (Semantic Search)", expanded=False):
        chunks = get_semantic_search_chunks(query, k=5)
        if chunks:
            st.write(f"Found {len(chunks)} relevant movies:")
            for i, chunk in enumerate(chunks, 1):
                st.write(f"**Chunk {i}:**")
                display_movie_card(chunk, show_chunk_info=True)
                st.divider()
        else:
            st.warning("No chunks retrieved or semantic search unavailable")
    
    # Extract information from response
    extracted_info = extract_movie_info(response)
    
    with st.expander("🎯 Information Extraction", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Extracted Titles:**")
            for title in extracted_info['titles']:
                st.write(f"• {title}")
        
        with col2:
            st.write("**Extracted Ratings:**")
            for rating in extracted_info['ratings']:
                st.write(f"• {rating}")
        
        with col3:
            st.write("**Extracted Years:**")
            for year in extracted_info['years']:
                st.write(f"• {year}")
    
    # Ground truth comparison
    ground_truth = load_ground_truth_data()
    if ground_truth:
        with st.expander("📊 Ground Truth Comparison", expanded=False):
            # Find matching ground truth entries
            query_lower = query.lower()
            matching_entries = []
            
            for entry in ground_truth:
                if any(word in query_lower for word in entry['query'].lower().split()):
                    matching_entries.append(entry)
            
            if matching_entries:
                st.write(f"Found {len(matching_entries)} matching ground truth entries:")
                
                for entry in matching_entries[:3]:  # Show top 3 matches
                    st.write(f"**Query:** {entry['query']}")
                    st.write(f"**Variable:** {entry['variable']}")
                    st.write(f"**Expected Value:** {entry['expected_value']}")
                    
                    # Compare with extracted values
                    if entry['variable'] == 'movie_title':
                        extracted_titles = extracted_info['titles']
                        if extracted_titles:
                            best_match = max(extracted_titles, 
                                           key=lambda x: similarity_score(x, str(entry['expected_value'])))
                            similarity = similarity_score(best_match, str(entry['expected_value']))
                            st.write(f"**Extracted:** {best_match} (Similarity: {similarity:.2f})")
                            if similarity > 0.8:
                                st.success("✅ Good match!")
                            else:
                                st.warning("⚠️ Partial match")
                    
                    elif entry['variable'] == 'avg_rating':
                        extracted_ratings = extracted_info['ratings']
                        if extracted_ratings:
                            expected = float(entry['expected_value'])
                            closest_rating = min(extracted_ratings, key=lambda x: abs(x - expected))
                            error = abs(closest_rating - expected)
                            st.write(f"**Extracted:** {closest_rating} (Error: {error:.2f})")
                            if error <= 0.5:
                                st.success("✅ Within tolerance!")
                            else:
                                st.error("❌ Outside tolerance")
                    
                    elif entry['variable'] == 'release_year':
                        extracted_years = extracted_info['years']
                        if extracted_years:
                            expected = int(entry['expected_value'])
                            if expected in extracted_years:
                                st.success(f"✅ Exact match: {expected}")
                            else:
                                closest_year = min(extracted_years, key=lambda x: abs(x - expected))
                                st.warning(f"⚠️ Closest: {closest_year} (Expected: {expected})")
                    
                    st.divider()
            else:
                st.info("No matching ground truth entries found for this query")
    else:
        st.info("Ground truth data not available")

def similarity_score(a: str, b: str) -> float:
    """Calculate similarity between two strings"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Main App
st.title("🎬 Movie Recommendation System")
st.markdown("*Intelligent movie recommendations using semantic search and natural language processing*")

# Check API status
if not check_api_health():
    st.error("⚠️ API is not running. Please start the server with: `python scripts/run_server.py`")
    st.stop()

st.success("✅ API is running!")

# Sidebar with sample queries and settings
st.sidebar.title("💡 Sample Queries")
sample_queries = [
    "Tell me about Inception",
    "Recommend sci-fi movies from 2010",
    "What are some good action movies?",
    "Find comedies with high ratings",
    "Movies similar to The Matrix"
]

for query in sample_queries:
    if st.sidebar.button(query, key=f"sample_{query}"):
        st.session_state.user_input = query

st.sidebar.markdown("---")
st.sidebar.title("⚙️ Settings")
show_rag_analysis = st.sidebar.checkbox(
    "🔍 Show RAG Analysis", 
    value=False,
    help="Display retrieved chunks and ground truth comparison"
)

# Main chat interface
st.header("💬 Movie Assistant")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input(
    "Ask me about movies:",
    value=st.session_state.get('user_input', ''),
    placeholder="e.g., 'Recommend action movies from 2020'"
)

if st.button("Send", type="primary") and user_input:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Show loading spinner
    with st.spinner("🤖 Thinking..."):
        result = chat_with_agent(user_input)
    
    if result and "error" not in result:
        # Add AI response to history
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": result['response'],
            "movies": result.get('movies', []),
            "intent": result.get('intent', ''),
            "params": result.get('params', {}),
            "query": user_input  # Store original query for RAG analysis
        })
    else:
        error_msg = result.get('error', 'Unknown error') if result else 'API request failed'
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": f"Sorry, I encountered an error: {error_msg}",
            "query": user_input
        })
    
    # Clear input
    st.session_state.user_input = ""

# Display chat history
st.header("💭 Conversation")
for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])
            
            # Show movies if available
            if "movies" in message and message["movies"]:
                st.subheader("🎬 Related Movies")
                for movie in message["movies"][:3]:  # Show top 3
                    display_movie_card(movie)
                    st.divider()
            
            # Show query analysis
            if "intent" in message and "params" in message:
                with st.expander("🔍 Query Analysis"):
                    st.write(f"**Intent**: {message['intent']}")
                    if message['params']:
                        st.write(f"**Parameters**: {message['params']}")
            
            # Show RAG analysis if enabled and query available
            if show_rag_analysis and "query" in message:
                display_rag_analysis(message["query"], message["content"])

# Additional features
st.header("🔍 Quick Movie Search")
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("Search movies by title:", placeholder="e.g., 'Inception'")

with col2:
    search_limit = st.selectbox("Results:", [5, 10, 20], index=0)

if st.button("Search") and search_query:
    with st.spinner("Searching..."):
        movies = search_movies(search_query, search_limit)
    
    if movies:
        st.subheader(f"Found {len(movies)} movies:")
        for movie in movies:
            display_movie_card(movie)
            st.divider()
    else:
        st.warning("No movies found.")

# Footer
st.markdown("---")
st.markdown("**Features Demonstrated:**")
st.markdown("- 🤖 Conversational AI with LLM (llama3.1:8b)")
st.markdown("- 🔍 Intelligent query processing and intent detection")
st.markdown("- 📊 SQLite database with MovieLens dataset")
st.markdown("- 🎯 RAG-powered semantic search with FAISS")
st.markdown("- 🔄 Hybrid search combining semantic + keyword matching")
st.markdown("- 📚 **RAG Chunk Visualization**: See retrieved movie chunks")
st.markdown("- 🎯 **Information Extraction**: Rule-based extraction from responses")
st.markdown("- 📊 **Ground Truth Comparison**: Evaluate against test dataset")
st.markdown("- ⚙️ **Evaluation Transparency**: Compare extracted vs expected values")