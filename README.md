# Financial Data Processing System

AI-powered financial data integration and analysis API that unifies diverse data sources and provides intelligent querying capabilities.

## 🎯 Overview

This system integrates financial data from QuickBooks and Rootfi formats, stores it in a unified database, and provides:
- RESTful API for data access
- Natural language querying powered by OpenAI
- AI-generated financial insights and narratives

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone and navigate to the project:**
```bash
cd kwtreca
```

2. **Install dependencies:**
```bash
make install
# OR
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Initialize database:**
```bash
make setup
# OR
python -c "from app.database import init_db; init_db()"
```

5. **Load financial data:**
```bash
make load-data
# OR
python load_data.py
```

6. **Start the API server:**
```bash
make run
# OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

Interactive API documentation at `http://localhost:8000/docs`

## 📡 API Endpoints

### Data Management

#### `POST /api/v1/data/load`
Load financial data from source files into database.

#### `GET /api/v1/data/periods`
Get all financial periods.
- Query params: `source` (optional) - Filter by 'quickbooks' or 'rootfi'

#### `GET /api/v1/data/periods/range`
Get periods within date range.
- Query params: `start_date`, `end_date` (YYYY-MM-DD), `source` (optional)

#### `GET /api/v1/data/summary`
Get summary statistics across all data.

### AI Features

#### `POST /api/v1/ai/query`
Natural language querying of financial data.

**Request:**
```json
{
  "question": "What was the total profit in Q1 2024?",
  "conversation_history": []
}
```

**Example Questions:**
- "What was the total profit in Q1?"
- "Show me revenue trends for 2024"
- "Which expense category had the highest increase this year?"
- "Compare Q1 and Q2 performance"

#### `POST /api/v1/ai/insights`
Generate AI-powered insights and narratives.

**Request:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User/Client                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │            API Layer (app/api.py)                 │  │
│  │  • RESTful endpoints                             │  │
│  │  • Request/Response validation (Pydantic)        │  │
│  └────────────┬─────────────────────────────────────┘  │
│               │                                          │
│  ┌────────────▼─────────────────────────────────────┐  │
│  │         Service Layer (app/services/)            │  │
│  │  ┌──────────────┐      ┌───────────────────┐   │  │
│  │  │ DataService  │      │   AIService       │   │  │
│  │  │ (CRUD ops)   │      │ (LLM integration) │   │  │
│  │  └──────┬───────┘      └─────────┬─────────┘   │  │
│  └─────────┼───────────────────────┼──────────────┘  │
│            │                        │                  │
│            ▼                        ▼                  │
│  ┌──────────────────┐    ┌──────────────────────┐    │
│  │  Database Layer  │    │   OpenAI GPT-4o-mini │    │
│  │  (SQLAlchemy)    │    │   (External API)     │    │
│  └─────────┬────────┘    └──────────────────────┘    │
└────────────┼──────────────────────────────────────────┘
             │
             ▼
   ┌──────────────────┐
   │ SQLite Database  │
   │ financial_data.db│
   └──────────────────┘
```

### Project Structure
```
kwtreca/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models.py            # Database models
│   ├── database.py          # Database setup
│   ├── schemas.py           # Pydantic schemas
│   ├── api.py               # API routes
│   ├── parsers/             # Data parsers
│   │   ├── quickbooks_parser.py
│   │   └── rootfi_parser.py
│   └── services/            # Business logic
│       ├── data_service.py
│       └── ai_service.py
├── data_ser-1.json          # QuickBooks data
├── data_set-2.json          # Rootfi data
├── load_data.py             # Data loading script
├── requirements.txt
├── Makefile
└── README.md
```

### Technology Stack
- **Framework:** FastAPI (modern, high-performance)
- **Database:** SQLite (simple, file-based)
- **ORM:** SQLAlchemy (robust data management)
- **AI/LLM:** OpenAI GPT-4o-mini (cost-effective, capable)
- **Validation:** Pydantic (type-safe schemas)

### Design Principles
- **Single Responsibility:** Each module has one clear purpose
- **Open/Closed:** Easily extensible for new data sources
- **Dependency Inversion:** Services depend on abstractions
- **Clean Architecture:** Separation of concerns (API, services, data)

## 🧪 Testing the API

### Using cURL

**Load data:**
```bash
curl -X POST http://localhost:8000/api/v1/data/load
```

**Get all periods:**
```bash
curl http://localhost:8000/api/v1/data/periods
```

**Natural language query:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What was the revenue in 2024?"}'
```

**Generate insights:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/insights \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2024-01-01", "end_date": "2024-12-31"}'
```

### Using Swagger UI
Navigate to `http://localhost:8000/docs` for interactive API documentation.

## 🤖 AI Features

### Natural Language Querying
The system uses OpenAI's GPT-4o-mini to:
1. Understand natural language questions
2. Access relevant financial data from the database
3. Generate clear, accurate responses with specific numbers
4. Support follow-up questions with conversation context

### Insights Generation
AI analyzes financial data to provide:
- Overall financial health assessment
- Revenue and profit trend analysis
- Expense pattern identification
- Notable observations and recommendations

## 📊 Data Sources

### QuickBooks Format (data_ser-1.json)
- Hierarchical P&L report structure
- Monthly columns from Jan 2020 to Aug 2025
- Detailed account breakdowns

### Rootfi Format (data_set-2.json)
- Array of monthly financial records
- Coverage: Aug 2022 to Jul 2025
- Nested line items structure

Both sources are unified into a consistent schema for seamless querying.

## 🔒 Environment Variables

Required in `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 🛠️ Development

### Clean up database and start fresh:
```bash
make clean
make setup
make load-data
```

### Run in production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📝 Known Limitations

1. **Data Overlaps:** Both sources have overlapping periods (Aug 2022 - Aug 2025). Currently stored as separate records with source differentiation.
2. **SQLite Limitations:** For production, consider PostgreSQL for concurrent access.
3. **AI Cost:** Natural language queries use OpenAI API (GPT-4o-mini for cost efficiency).
4. **Context Window:** Very long conversations may exceed LLM context limits.

## 🚀 Deployment

### Local Development
```bash
make run
```

### Docker Deployment
```bash
docker-compose up --build
```

### Production Deployment (Render.com)
1. Create new Web Service
2. Set environment variable: `OPENAI_API_KEY`
3. Build command: `pip install -r requirements.txt && python -c "from app.database import init_db; init_db()" && python load_data.py`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables
Required for production:
```
OPENAI_API_KEY=your_openai_api_key
```

## 📖 Documentation

- **Quick Start:** See `QUICK_START.md` for 5-minute setup guide
- **API Examples:** See `EXAMPLES.md` for comprehensive API usage examples
- **Technical Details:** See `TECHNICAL_REPORT.md` for architecture and design decisions

## 🧪 Testing

Run the test script (requires API to be running):
```bash
python test_system.py
```

## 🎯 What Makes This Special

### AI-First Approach
- Natural language querying with conversation support
- Automated insights generation
- Cost-optimized with GPT-4o-mini
- Real-world applicable features

### Production Quality
- Clean Architecture with SOLID principles
- Comprehensive error handling
- Input validation throughout
- Deployment ready with guides

### Developer Experience
- Setup in < 2 minutes
- Interactive API documentation
- Test script included
- Multiple documentation levels

## 🤝 About This Project

This is a take-home test project for Kudwa, demonstrating:
- AI/ML integration expertise
- Backend architecture skills
- Production-ready development practices
- Comprehensive documentation abilities

**All mandatory requirements met + bonus features included!**

## 📄 License

Proprietary - Kudwa Take-Home Test

---

**Ready to explore?** Start with `QUICK_START.md` or jump straight to `http://localhost:8000/docs` after setup! 🚀

