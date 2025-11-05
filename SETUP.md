# Setup Instructions

## Quick Setup (Automated)

```bash
# Clone the repository
git clone <repository-url>
cd movies-agent

# Run automated setup
python setup.py
```

## Manual Setup

### 1. Prerequisites
- Python 3.11 or higher
- Git
- 8GB+ RAM recommended

### 2. Installation

```bash
# Clone repository
git clone <repository-url>
cd movies-agent

# Install dependencies
pip install -r requirements.txt

# Setup environment (optional)
cp .env.example .env

# Initialize database and load data
python scripts/setup_data.py
```

### 3. Start the System

```bash
# Start API server
python scripts/run_server.py

# API will be available at: http://localhost:8000
# API documentation at: http://localhost:8000/docs
```

### 4. Run Demo Application

```bash
# In a new terminal, start Streamlit demo
streamlit run streamlit_demo.py

# Demo will open in browser at: http://localhost:8501
```

## Docker Setup (Alternative)

```bash
# Build and run with Docker
docker-compose up --build

# Access API at: http://localhost:8000
```

## Testing the System

### Basic API Test
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test movie query
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Inception"}'
```

### Run Evaluation
```bash
python scripts/run_evaluation.py
```

## Optional: Enhanced LLM Responses

For better conversational responses, install Ollama:

1. **Download Ollama**: https://ollama.ai
2. **Install model**: `ollama pull llama3.1:8b`
3. **Start service**: `ollama serve`

The system will automatically use Ollama if available, otherwise falls back to basic responses.

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in .env file
   API_PORT=8001
   ```

2. **Database errors**
   ```bash
   # Reinitialize database
   rm data/processed/movies.db
   python scripts/setup_data.py
   ```

3. **Missing dependencies**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

### System Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 2GB for dataset and embeddings

## Usage Examples

### Sample Queries
- "Tell me about Inception"
- "Recommend sci-fi movies from 2010"
- "What are some good action movies?"
- "Find comedies with high ratings"
- "Movies similar to The Matrix"

### API Endpoints
- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - Conversational queries
- `GET /api/v1/movies/search` - Movie search
- `GET /api/v1/movies/semantic-search` - Semantic search

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the terminal output
3. Ensure all prerequisites are installed
4. Verify the database was created successfully