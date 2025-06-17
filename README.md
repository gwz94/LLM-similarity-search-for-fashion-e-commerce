# openAI_assignment

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── ai_utils/                   # AI and machine learning utilities
│   │   │   ├── __init__.py             
│   │   │   ├── embeddings.py           # Text embedding generation using OpenAI
│   │   │   └── llm_reranker.py         # LLM-based search result reranking
│   │   ├── config/                     # Application configuration
│   │   │   ├── __init__.py             
│   │   │   └── settings.py             # Environment and application settings
│   │   ├── database/                   # Database operations
│   │   │   ├── __init__.py             
│   │   │   ├── Dockerfile              # Database container configuration for database
│   │   │   ├── insert_data.py          # Product data insertion and preprocessing
│   │   │   └── vector_db.py            # Vector database operations
│   │   ├── deps/                       # Dependency injection
│   │   │   ├── __init__.py             
│   │   │   └── db.py                   # Database connection management
│   │   ├── preprocessing/              # Data preprocessing pipeline
│   │   │   ├── __init__.py             
│   │   │   ├── data_cleaning.py        # Data cleaning and normalization
│   │   │   ├── embedding_generation.py # Product embedding generation
│   │   │   ├── preprocess_pipeline.py  # Data preprocessing pipeline
│   │   │   └── product_image_feature_extraction.py # Image feature extraction
│   │   ├── schemas/                    # Data validation schemas
│   │   │   ├── __init__.py             
│   │   │   └── query_shema.py          # Search query validation
│   │   ├── utils/                      # Utility functions
│   │   │   ├── __init__.py             
│   │   │   └── logger.py               # Logging configuration
│   │   └── main.py                     # FastAPI application entry point
│   ├── tests/                          # Test suite
│   │   ├── __init__.py                 
│   │   ├── conftest.py                 # Test configuration and fixtures
│   │   └── test_search.py              # Search functionality tests
│   ├── Dockerfile                      # Backend production container
│   └── requirements.txt                # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/                 # React components
│   │   │   ├── ui/                     # Reusable UI components
│   │   │   │   ├── ai-insight.tsx      # AI insight display component
│   │   │   │   ├── product-card.tsx    # Product card component
│   │   │   │   └── product-carousel.tsx # Image carousel component
│   │   │   ├── PageSkeleton.tsx        # Loading skeleton component
│   │   │   ├── SearchBox.tsx           # Search input component
│   │   │   ├── SearchForm.tsx          # Search form component
│   │   │   └── SearchResults.tsx       # Search results display
│   │   ├── services/                   # API services
│   │   │   └── api.ts                  # API client and endpoints
│   │   ├── types/                      # TypeScript type definitions
│   │   │   └── product.ts              # Product interface definitions
│   │   ├── app/                        # Next.js app directory
│   │   │   └── page.tsx                # Main page component
│   │   └── globals.css                 # Global styles
│   ├── public/                         # Static assets
│   │   └── favicon.ico                 # Site favicon
│   ├── Dockerfile                      # Frontend production container
│   ├── Dockerfile.dev                  # Frontend development container
│   ├── next.config.js                  # Next.js configuration
│   ├── next-env.d.ts                   # Next.js TypeScript definitions
│   ├── package.json                    # Node.js dependencies
│   ├── package-lock.json               # Dependency lock file
│   ├── postcss.config.js               # PostCSS configuration
│   ├── tailwind.config.ts              # Tailwind CSS configuration
│   └── tsconfig.json                   # TypeScript configuration
│
├── docker-compose.yml                  # Docker services configuration
├── startup.sh                          # Application startup script
└── README.md                           # Project documentation
```

### Key Components

#### Backend
- **AI Utils**: Handles embeddings generation and search result reranking
- **Database**: Manages vector database operations and product data
- **Preprocessing**: Data cleaning and preparation pipeline
- **Schemas**: Request/response validation and type definitions

#### Frontend
- **Components**: React components for the user interface
- **Services**: API integration and data fetching
- **UI Components**: Reusable UI elements (carousel, cards, etc.)

#### Configuration
- **Docker**: Separate configurations for development and production
- **Startup Script**: Automated deployment and initialization