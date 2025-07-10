# AI-Powered Fashion Search Application

A modern e-commerce search application that uses OpenAI GPT models for semantic similarity search and personalized product recommendations. Built with FastAPI backend, Next.js frontend, and PostgreSQL with vector search capabilities.

## 🚀 Features

- **AI-Powered Search**: Semantic search using OpenAI embeddings
- **Smart Recommendations**: LLM-based result reranking and personalized suggestions
- **Stock Management**: Separate handling of in-stock and out-of-stock products
- **Modern UI**: Responsive design with Tailwind CSS and product carousels
- **Easy Deployment**: Docker containerization with automated setup

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Set Up Your OpenAI API Key

Create environment files for your API key:

```bash
# For production
echo "OPENAI_API_KEY=your_openai_api_key_here" > backend/.env.production

# For development (optional)
echo "OPENAI_API_KEY=your_openai_api_key_here" > backend/.env.development
```

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 3. Start the Application

```bash
# For production
./startup.sh prod

# For development
./startup.sh dev
```

**Note**: Initial data insertion may take approximately 30 minutes for the full dataset. You can reduce processing time by modifying the `DATA_LOAD_FRACTION` in `backend/app/config/settings.py`.

### 4. Access the Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001

## 🏗️ Project Structure

```
.
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── ai_utils/          # AI utilities (embeddings, LLM reranking)
│   │   ├── config/            # Application configuration
│   │   ├── database/          # Database operations
│   │   ├── preprocessing/     # Data preprocessing pipeline
│   │   ├── schemas/           # Data validation schemas
│   │   └── main.py           # FastAPI application
│   ├── tests/                 # Test suite
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   └── types/            # TypeScript definitions
│   └── package.json          # Node.js dependencies
├── docker-compose.yml         # Docker services configuration
└── startup.sh                # Application startup script
```

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DATA_LOAD_FRACTION`: Fraction of data to load (default: 0.5)
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)

### Data Loading

The application processes Amazon Fashion product data. You can:

1. **Download the required dataset** (recommended for full functionality):
   ```bash
   # Create the raw_data directory if it doesn't exist
   mkdir -p raw_data
   
   # Download the Amazon Fashion dataset
   curl -L "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_Amazon_Fashion.jsonl.gz" -o raw_data/meta_Amazon_Fashion.jsonl.gz
   
   # Extract the compressed file
   gunzip raw_data/meta_Amazon_Fashion.jsonl.gz
   ```

2. **Use the provided sample data** (for testing without downloading the full dataset)
3. **Add your own data** by placing JSONL files in the `raw_data/` directory

**Note**: The full dataset is approximately 1.2GB when extracted. For faster testing, you can use the sample data or reduce the `DATA_LOAD_FRACTION` in `backend/app/config/settings.py`.

## 📚 API Documentation

### Base URL
- **Local Development**: `http://localhost:8001`
- **Production**: `http://[your-domain]:8001`

### Endpoints

#### Health Check
```bash
GET /health
```

#### Search Products
```bash
POST /search
```

**Request Body:**
```json
{
  "query": "comfortable running shoes for women",
  "top_k": 10
}
```

**Response:**
```json
{
  "status": "success",
  "recommended_in_stock_products": [...],
  "recommended_out_of_stock_products": [...]
}
```

### Example API Calls

#### Using cURL
```bash
# Search for products
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "comfortable running shoes for women",
    "top_k": 5
  }'
```

#### Using Python
```python
import requests

search_data = {
    "query": "comfortable running shoes for women",
    "top_k": 5
}
response = requests.post("http://localhost:8001/search", json=search_data)
results = response.json()
```

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 🐳 Docker Deployment

The application is containerized with Docker:

- **Backend**: FastAPI with Python 3.11
- **Frontend**: Next.js with Node.js
- **Database**: PostgreSQL with pgvector extension

### Production Deployment

1. Set your OpenAI API key in `backend/.env.production`
2. Run: `./startup.sh prod`
3. Access at http://localhost:3001

### Development Deployment

1. Set your OpenAI API key in `backend/.env.development`
2. Run: `./startup.sh dev`
3. Access at http://localhost:3001

## 🔍 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your OpenAI API key is correctly set in the environment files
2. **Data Loading Time**: Reduce `DATA_LOAD_FRACTION` in settings for faster startup
3. **Port Conflicts**: Check if ports 3001 and 8001 are available
4. **Docker Issues**: Ensure Docker and Docker Compose are properly installed

### Logs

Check application logs:
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs database
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

