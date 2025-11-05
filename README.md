# Movie Recommendation Agent

A conversational AI system that provides intelligent movie recommendations and information using the MovieLens dataset, advanced RAG (Retrieval-Augmented Generation) pipeline, and large language models.

## 🎯 Features

- **Conversational Interface**: Natural language movie queries and recommendations
- **RAG-Powered Search**: Semantic similarity search using FAISS vector embeddings
- **Hybrid Retrieval**: Combines semantic search with traditional database filtering
- **LLM Integration**: Ollama integration for natural, contextual responses
- **Comprehensive Evaluation**: Built-in testing framework with ground truth validation
- **Interactive Demo**: Streamlit web interface with RAG analysis visualization

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Query Processor │───▶│  Intent & Params│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  LLM Response   │◀───│   RAG Pipeline   │───▶│ Vector Search   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Movie Database   │    │ FAISS Index     │
                       │ (SQLite)         │    │ (Embeddings)    │
                       └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd movies-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize the database**
```bash
python scripts/setup_data.py
```

4. **Start the API server**
```bash
python scripts/run_server.py
```

The API will be available at `http://localhost:8000`

### 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access API at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## 🎬 Demo Application

### Start the Interactive Demo
```bash
# Ensure API is running first
python scripts/run_server.py

# In another terminal, start Streamlit demo
streamlit run streamlit_demo.py
```

### Demo Features
- **💬 Chat Interface**: Ask natural language questions about movies
- **🔍 Advanced Analysis**: View RAG chunks and information extraction
- **📊 Ground Truth Comparison**: See how responses match expected results
- **🎯 Sample Queries**: Pre-built examples to explore capabilities

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Main conversational endpoint |
| `GET` | `/api/v1/movies/search` | Search movies with filters |
| `GET` | `/api/v1/movies/semantic-search` | Semantic similarity search |
| `GET` | `/api/v1/movies/{id}` | Get specific movie details |
| `GET` | `/api/v1/health` | Health check |

### Example Usage

```bash
# Ask about a specific movie
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Inception"}'

# Get movie recommendations
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Recommend sci-fi movies from 2010"}'

# Search movies by title
curl "http://localhost:8000/api/v1/movies/search?q=matrix&limit=5"
```

## 🧪 Evaluation System

### Run Comprehensive Evaluation
```bash
python scripts/run_evaluation.py
```

### Evaluation Metrics
- **Information Extraction**: Tests extraction of movie titles, ratings, and years
- **Ground Truth Validation**: Compares responses against known correct answers
- **RAG Performance**: Measures retrieval quality and response accuracy
- **Success Rate**: Overall system reliability

### Sample Results
```
============================================================
MOVIE EVALUATION PIPELINE RESULTS
============================================================
Total Observations: 15
Success Rate: 100.0%
Average Groundedness: 0.85
Average Truthfulness: 0.73

VARIABLE-SPECIFIC METRICS:
MOVIE_TITLE: 100.0% accuracy
AVG_RATING: 80.0% tolerance accuracy  
RELEASE_YEAR: 100.0% exact accuracy
============================================================
```

## 🛠️ Configuration

### Environment Variables
Create a `.env` file:
```bash
DATABASE_URL=sqlite:///./data/processed/movies.db
OLLAMA_BASE_URL=http://localhost:11434
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### LLM Setup (Optional)
For enhanced responses, install Ollama:
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.1:8b
ollama serve
```

## 📊 Dataset

- **Source**: MovieLens Small Dataset (~100k ratings, ~9k movies)
- **Storage**: SQLite database with optimized schema
- **Features**: Movies, ratings, genres, cast, directors, plot summaries
- **Embeddings**: Sentence transformer embeddings for semantic search

## 🔧 Development

### Project Structure
```
movies-agent/
├── app/
│   ├── api/           # FastAPI routes and schemas
│   ├── database/      # Database models and connections
│   ├── services/      # Business logic (RAG, LLM, embeddings)
│   └── main.py        # FastAPI application
├── scripts/           # Setup and utility scripts
├── data/             # Database and processed files
├── tests/            # Unit and integration tests
└── streamlit_demo.py # Interactive demo application
```

### Key Components

1. **RAG Pipeline** (`app/services/rag_service.py`)
   - Orchestrates semantic search and LLM generation
   - Handles fallback to traditional database queries

2. **Vector Store** (`app/services/vector_store.py`)
   - FAISS-based similarity search
   - Hybrid search combining semantic and keyword matching

3. **Evaluation Framework** (`app/services/evaluation_*.py`)
   - Rule-based information extraction
   - Ground truth comparison and metrics calculation

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run evaluation pipeline
python scripts/run_evaluation.py

# Test API endpoints
curl http://localhost:8000/api/v1/health
```

## 📈 Performance

### System Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **With Ollama**: Additional 8GB RAM for LLM

### Response Times
- **Database queries**: <100ms
- **Semantic search**: 200-500ms
- **LLM generation**: 10-30s (depending on model)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MovieLens dataset by GroupLens Research
- LangChain framework for RAG implementation
- Ollama for local LLM inference
- FastAPI for the REST API framework