# Deployment Guide

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Ollama running on host machine (optional, for enhanced responses)

### Quick Start
```bash
# 1. Clone repository
git clone <repository-url>
cd movies-agent

# 2. Set up environment
cp .env.example .env

# 3. Initialize data (one-time setup)
python scripts/setup_data.py

# 4. Build and run with Docker
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### With Ollama Integration
```bash
# Start Ollama on host
ollama serve
ollama pull llama3.1:8b

# Run the application
docker-compose up --build
```

## 🖥️ Local Development

### Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python scripts/setup_data.py

# 3. Start API server
python scripts/run_server.py

# 4. (Optional) Start Streamlit demo
streamlit run streamlit_demo.py
```

## 🎬 Streamlit Demo

### Running the Demo
```bash
# Ensure API is running first
python scripts/run_server.py

# In another terminal, start Streamlit
streamlit run streamlit_demo.py
```

### Demo Features
- **Interactive Chat**: Conversational movie queries
- **Sample Queries**: Pre-built examples to try
- **Movie Search**: Quick title-based search
- **Query Analysis**: Shows intent detection and parameters
- **Movie Cards**: Rich movie information display

### Sample Interactions
1. **Movie Information**: "Tell me about Inception"
2. **Recommendations**: "Recommend sci-fi movies from 2010"
3. **Filtered Search**: "Find action movies with high ratings"
4. **Similarity**: "Movies similar to The Matrix"

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./data/processed/movies.db
OLLAMA_BASE_URL=http://localhost:11434
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### Ollama Models
- **llama3.1:8b** (Recommended): Best balance of quality and speed
- **llama3.2:1b**: Faster responses, good for high volume
- **llama2**: Fallback option

## 📊 Performance Optimization

### For Production
1. **Use faster models**: llama3.2:1b for speed
2. **Increase timeouts**: Adjust based on model performance
3. **Cache responses**: Implement Redis for frequent queries
4. **Load balancing**: Multiple API instances behind proxy

### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **With Ollama**: Additional 8GB RAM for model

## 🧪 Testing

### API Testing
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat endpoint
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Inception"}'

# Movie search
curl "http://localhost:8000/api/v1/movies/search?q=inception"
```

### Evaluation Pipeline
```bash
# Run comprehensive evaluation
python scripts/run_evaluation.py
```

## 🚀 Production Deployment

### Docker Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  movie-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=WARNING
      - API_HOST=0.0.0.0
    restart: always
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: movie-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: movie-agent
  template:
    metadata:
      labels:
        app: movie-agent
    spec:
      containers:
      - name: movie-agent
        image: movie-agent:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## 🔍 Monitoring

### Health Checks
- **API Health**: `GET /api/v1/health`
- **Database**: Automatic connection testing
- **Ollama**: Fallback to basic responses if unavailable

### Logging
- **Structured logging** with timestamps
- **Request/response tracking**
- **Error monitoring** with stack traces
- **Performance metrics** for response times

## 🛠️ Troubleshooting

### Common Issues
1. **Ollama timeout**: Increase timeout or use faster model
2. **Database locked**: Ensure single writer access
3. **Memory issues**: Reduce model size or increase resources
4. **Port conflicts**: Change API_PORT in .env

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python scripts/run_server.py
```