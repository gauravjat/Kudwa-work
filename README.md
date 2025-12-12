# Financial Data Analysis System with LangChain

AI-powered financial data integration and analysis API that unifies diverse data sources and provides intelligent querying capabilities using **LangChain** and **Jinja2 templates**.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [LangChain Architecture](#-langchain-architecture)
- [Prompt Templates](#-prompt-templates)
- [Technology Stack](#-technology-stack)
- [Testing](#-testing)

---

## 🎯 Overview

This system integrates financial data from QuickBooks and Rootfi formats into a unified database and provides:
- **RESTful API** for data access and management
- **Natural Language Querying** powered by LangChain + OpenAI
- **AI-Generated Insights** using template-based prompts
- **Production-Ready Architecture** with clean code practices

### Key Features
✅ LangChain integration for flexible LLM interactions  
✅ Jinja2 template-based prompt management  
✅ Conversation history with context awareness  
✅ Type-safe message handling (SystemMessage, HumanMessage, AIMessage)  
✅ Easy to extend with chains, agents, and memory  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Docker (optional)

### Installation

**Option 1: Docker (Recommended)**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Start the service
docker compose up --build
```

**Option 2: Local Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
EOF

# Initialize database and load data
python -c "from app.database import init_db; init_db()"
python load_data.py

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access the API:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

---

## 📡 API Endpoints

### Data Management

#### 1. Load Financial Data
```http
POST /api/v1/data/load
```

Loads financial data from QuickBooks and Rootfi source files into the database.

**Response:**
```json
{
  "message": "Data loaded successfully",
  "quickbooks_records": 52,
  "rootfi_records": 52,
  "total_records": 104
}
```

#### 2. Get All Financial Periods
```http
GET /api/v1/data/periods?source=quickbooks
```

**Query Parameters:**
- `source` (optional): Filter by `quickbooks` or `rootfi`

**Response:**
```json
[
  {
    "id": 1,
    "period_start": "2024-01-01",
    "period_end": "2024-01-31",
    "revenue": 4636050.60,
    "operating_expenses": 4102114.53,
    "net_profit": 461459.50,
    "source": "rootfi"
  }
]
```

#### 3. Get Periods by Date Range
```http
GET /api/v1/data/periods/range?start_date=2024-01-01&end_date=2024-12-31
```

**Query Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `source` (optional): Filter by data source

#### 4. Get Summary Statistics
```http
GET /api/v1/data/summary
```

**Response:**
```json
{
  "total_periods": 104,
  "date_range": {
    "start": "2020-01-01",
    "end": "2025-08-31"
  },
  "total_revenue": 161029030.56,
  "total_expenses": 146033303.39,
  "total_profit": 2757234.28,
  "average_revenue": 1548356.06,
  "average_expenses": 1404166.38,
  "average_profit": 26511.87
}
```

---

### AI Features

#### 5. Natural Language Query
```http
POST /api/v1/ai/query
Content-Type: application/json
```

Ask questions about financial data in natural language.

**Request Body:**
```json
{
  "question": "What was the total profit in Q1 2024?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous question"
    },
    {
      "role": "assistant",
      "content": "Previous answer"
    }
  ]
}
```

**Example Questions:**
- "What was the total profit in Q1 2024?"
- "Show me revenue trends for 2024"
- "Which expense category had the highest increase?"
- "Compare Q1 and Q2 performance"
- "How is our financial health?"

**Response:**
```json
{
  "answer": "Based on the data, Q1 2024 shows...",
  "supporting_data": {
    "periods": [
      {
        "period": "2024-01-01 to 2024-01-31",
        "revenue": 4636050.60,
        "expenses": 4102114.53,
        "profit": 461459.50
      }
    ]
  },
  "question": "What was the total profit in Q1 2024?",
  "timestamp": "2025-12-12T12:00:00.000000"
}
```

#### 6. Generate AI Insights
```http
POST /api/v1/ai/insights
Content-Type: application/json
```

Generate comprehensive AI-powered financial insights.

**Request Body (Optional):**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Response:**
```json
{
  "insights": "### 1. Overall Financial Health\n- Net profit of $2.7M indicates...",
  "period_count": 104,
  "data_summary": {
    "totals": {
      "revenue": 161029030.56,
      "expenses": 146033303.39,
      "profit": 2757234.28
    },
    "averages": {
      "revenue": 1548356.06,
      "expenses": 1404166.38,
      "profit": 26511.87
    },
    "trends": {
      "revenue_trend": [5376812.01, 1521316.57, ...],
      "profit_trend": [488801.10, 680455.76, ...]
    }
  },
  "timestamp": "2025-12-12T12:00:00.000000"
}
```

---

## 🏗️ LangChain Architecture

### How LangChain Integration Works

#### 1. **Traditional OpenAI (Before)**
```python
from openai import OpenAI

client = OpenAI(api_key="...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "question"}]
)
```

**Issues:**
- Direct API coupling
- Hard to switch providers
- No built-in conversation management
- Manual prompt engineering in code

#### 2. **LangChain Approach (Current)**
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    openai_api_key=settings.OPENAI_API_KEY
)

# Build messages with proper types
messages = [
    SystemMessage(content="You are a financial analyst..."),
    HumanMessage(content="What was the profit?")
]

# Invoke LLM
response = llm.invoke(messages)
answer = response.content
```

**Benefits:**
- ✅ Provider-agnostic (easy to switch to Anthropic, etc.)
- ✅ Type-safe message handling
- ✅ Built-in conversation memory support
- ✅ Extensible with chains and agents
- ✅ Better error handling and retries

### Architecture Flow

```
┌─────────────────────────────────────────────────────────┐
│                   User Request                          │
│          "What was the profit in Q1?"                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Endpoint                           │
│             /api/v1/ai/query                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               AIService                                 │
│  1. Fetch financial data from database                 │
│  2. Load Jinja2 prompt templates                       │
│  3. Render templates with data                         │
│  4. Build LangChain messages                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│             Prompt Templates (Jinja2)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ system_prompt.j2                                 │  │
│  │ "You are a financial analyst..."                 │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ financial_context.j2                             │  │
│  │ "Total Revenue: ${{ total_revenue }}"            │  │
│  │ "Recent periods: {% for p in periods %}..."      │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         LangChain ChatOpenAI                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │ SystemMessage: "You are a financial analyst"     │  │
│  │ SystemMessage: "Financial Context: ..."          │  │
│  │ HumanMessage: "What was the profit in Q1?"       │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           OpenAI GPT-4o-mini API                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AI Response                                │
│  "Q1 2024 profit was $1,145,848.97..."                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         JSON Response to User                           │
│  {                                                      │
│    "answer": "...",                                     │
│    "supporting_data": {...},                           │
│    "timestamp": "..."                                   │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

### Code Implementation

**File: `app/services/ai_service.py`**

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.prompts.prompt_loader import prompt_loader

class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
        
        # Initialize LangChain LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY,
            max_tokens=1000
        )
    
    def query_natural_language(self, question: str, 
                               conversation_history: List[Dict] = None):
        # 1. Get financial data
        financial_context = self._prepare_financial_context()
        
        # 2. Build messages with LangChain types
        messages = self._build_langchain_messages(
            question, 
            financial_context, 
            conversation_history
        )
        
        # 3. Invoke LLM
        response = self.llm.invoke(messages)
        
        # 4. Extract supporting data
        supporting_data = self._extract_supporting_data(question)
        
        return {
            'answer': response.content,
            'supporting_data': supporting_data,
            'question': question,
            'timestamp': datetime.now().isoformat()
        }
    
    def _build_langchain_messages(self, question, context, history):
        # Load system prompt from Jinja2 template
        system_prompt = prompt_loader.get_system_prompt()
        
        messages = [
            SystemMessage(content=system_prompt),
            SystemMessage(content=context)
        ]
        
        # Add conversation history
        if history:
            for msg in history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))
        
        # Add current question
        messages.append(HumanMessage(content=question))
        
        return messages
```

---

## 📝 Prompt Templates

All prompts are managed as Jinja2 templates in `app/prompts/` for easy maintenance and version control.

### Folder Structure
```
app/prompts/
├── __init__.py
├── system_prompt.j2           # AI assistant role definition
├── financial_context.j2        # Data context template
├── insights_prompt.j2          # Insights generation template
└── prompt_loader.py            # Template loader utility
```

### 1. System Prompt (`system_prompt.j2`)
Defines the AI assistant's behavior and guidelines.

```jinja2
You are a financial data analyst assistant specialized in analyzing 
financial data and providing clear, actionable insights.

Your responsibilities:
- Answer questions about financial data with precision and clarity
- Always include specific numbers, percentages, and time periods
- Provide context and comparisons to help users understand trends
- If you cannot find the exact answer, clearly state what's missing
- Format monetary values properly (e.g., $1,234.56)

Important guidelines:
- Base your answers ONLY on the provided financial data context
- Do not make assumptions or provide information not in the data
- Focus on actionable insights rather than just stating numbers
```

### 2. Financial Context (`financial_context.j2`)
Dynamically renders financial data for the AI.

```jinja2
Financial Data Context:

Dataset Overview:
- Total Periods: {{ total_periods }}
- Date Range: {{ date_range_start }} to {{ date_range_end }}
- Total Revenue: ${{ "%.2f"|format(total_revenue) }}
- Total Expenses: ${{ "%.2f"|format(total_expenses) }}
- Total Net Profit: ${{ "%.2f"|format(total_profit) }}

{% if recent_periods %}
Recent Monthly Data (Last {{ recent_periods|length }} months):
{% for period in recent_periods %}
- {{ period.period_start }} to {{ period.period_end }}:
  Revenue: ${{ "%.2f"|format(period.revenue) }}, 
  Expenses: ${{ "%.2f"|format(period.operating_expenses) }}, 
  Net Profit: ${{ "%.2f"|format(period.net_profit) }}
{% endfor %}
{% endif %}
```

### 3. Insights Prompt (`insights_prompt.j2`)
Template for generating comprehensive insights.

```jinja2
Analyze the following financial data and provide 3-5 key insights.

Period: {{ date_range_start }} to {{ date_range_end }}
Number of Periods: {{ period_count }}

Financial Summary:
- Total Revenue: ${{ "%.2f"|format(total_revenue) }}
- Total Expenses: ${{ "%.2f"|format(total_expenses) }}
- Total Net Profit: ${{ "%.2f"|format(total_profit) }}
- Profit Margin: {{ "%.1f"|format(profit_margin) }}%

Monthly Averages:
- Average Revenue: ${{ "%.2f"|format(avg_revenue) }}
- Average Expenses: ${{ "%.2f"|format(avg_expenses) }}
- Average Profit: ${{ "%.2f"|format(avg_profit) }}

Please provide insights covering:
1. Overall Financial Health
2. Revenue and Profit Trends
3. Expense Management
4. Key Observations
5. Recommendations
```

### 4. Prompt Loader (`prompt_loader.py`)
Utility for loading and rendering templates.

```python
from jinja2 import Environment, FileSystemLoader

class PromptLoader:
    def __init__(self):
        template_dir = os.path.dirname(os.path.abspath(__file__))
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def get_system_prompt(self) -> str:
        return self.render('system_prompt.j2', {})
    
    def get_financial_context(self, context: Dict[str, Any]) -> str:
        return self.render('financial_context.j2', context)

# Global instance
prompt_loader = PromptLoader()
```

**Benefits of Jinja2 Templates:**
- ✅ Separation of prompts from code
- ✅ Easy to version control and modify
- ✅ Supports variables, loops, conditionals
- ✅ Can be tested independently
- ✅ Team members can update prompts without coding

---

## 💻 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | Modern, high-performance web framework |
| **Database** | SQLite | Simple, file-based database |
| **ORM** | SQLAlchemy | Robust data management |
| **AI Framework** | LangChain | Flexible LLM integration |
| **LLM** | OpenAI GPT-4o-mini | Cost-effective, capable model |
| **Prompts** | Jinja2 | Template-based prompt management |
| **Validation** | Pydantic | Type-safe request/response schemas |
| **Containerization** | Docker | Easy deployment |

### Project Structure
```
Kudwa-work/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration (env vars)
│   ├── models.py               # SQLAlchemy models
│   ├── database.py             # Database setup
│   ├── schemas.py              # Pydantic schemas
│   ├── api.py                  # API routes
│   ├── exceptions.py           # Custom exceptions
│   ├── validators.py           # Data validation
│   ├── parsers/                # Data source parsers
│   │   ├── quickbooks_parser.py
│   │   └── rootfi_parser.py
│   ├── prompts/                # Jinja2 templates
│   │   ├── system_prompt.j2
│   │   ├── financial_context.j2
│   │   ├── insights_prompt.j2
│   │   └── prompt_loader.py
│   └── services/               # Business logic
│       ├── data_service.py
│       └── ai_service.py       # LangChain integration
├── data/                       # Financial datasets
│   ├── data_set_1.json         # QuickBooks data
│   └── data_set_2.json         # Rootfi data
├── load_data.py                # Data loading script
├── test_langchain.py           # Test script
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Docker compose config
├── .gitignore                  # Git ignore rules
├── Makefile                    # Common commands
└── README.md                   # This file
```

---

## 🧪 Testing

### Manual Testing with cURL

**1. Load Data:**
```bash
curl -X POST http://localhost:8000/api/v1/data/load
```

**2. Get Summary:**
```bash
curl http://localhost:8000/api/v1/data/summary
```

**3. Natural Language Query:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was the total profit in Q1 2024?"
  }'
```

**4. Generate Insights:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/insights \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

### Automated Test Script

Run the included test script:
```bash
python test_langchain.py
```

This will test all endpoints and verify the LangChain integration.

### Interactive API Documentation

Navigate to http://localhost:8000/docs for Swagger UI where you can:
- See all available endpoints
- Test API calls directly in browser
- View request/response schemas
- Download OpenAPI specification

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Important:** Never commit the `.env` file to version control. It's already in `.gitignore`.

### Docker Configuration

The `docker-compose.yml` file includes:
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=gpt-4o-mini
    volumes:
      - ./financial_data.db:/app/financial_data.db
```

---

## 🚀 Deployment

### Local Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production with Docker
```bash
docker compose up -d
```

### Cloud Deployment (Render.com)
1. Create new Web Service
2. Connect your GitHub repository
3. Set environment variable: `OPENAI_API_KEY`
4. Build command: `pip install -r requirements.txt && python -c "from app.database import init_db; init_db()" && python load_data.py`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📊 Data Sources

### QuickBooks Format (`data/data_set_1.json`)
- Hierarchical P&L report structure
- Monthly columns from Jan 2020 to Aug 2025
- Detailed account breakdowns

### Rootfi Format (`data/data_set_2.json`)
- Array of monthly financial records
- Coverage: Aug 2022 to Jul 2025
- Nested line items structure

Both sources are unified into a consistent schema for seamless querying.

---

## 🔍 Key Implementation Details

### Why LangChain?
1. **Provider Flexibility**: Easy to switch between OpenAI, Anthropic, Cohere, etc.
2. **Type Safety**: Proper message types prevent common errors
3. **Extensibility**: Built-in support for chains, agents, memory
4. **Production Ready**: Better error handling, retries, callbacks
5. **Future Proof**: Ecosystem of tools and integrations

### Why Jinja2 Templates?
1. **Separation of Concerns**: Prompts live in templates, not code
2. **Easy Iteration**: Modify prompts without changing Python
3. **Version Control**: Track prompt changes over time
4. **Team Collaboration**: Non-developers can update prompts
5. **Testing**: Templates can be tested independently

### Conversation Management
- History is sanitized and limited to last 10 messages
- Proper message type conversion (user → HumanMessage)
- Context window management to avoid token limits
- Support for follow-up questions with full context

---

## ⚠️ Known Limitations

1. **Data Overlaps**: Both sources have overlapping periods - stored as separate records
2. **SQLite**: Single-user database; consider PostgreSQL for production
3. **API Costs**: Uses OpenAI API (GPT-4o-mini is cost-optimized)
4. **Context Limits**: Very long conversations may need truncation

---

## 📝 License

Proprietary - Kudwa Take-Home Test

---

## 🎯 Quick Reference

**Start Server:**
```bash
docker compose up
```

**API Base URL:**
```
http://localhost:8000
```

**Interactive Docs:**
```
http://localhost:8000/docs
```

**Test Everything:**
```bash
python test_langchain.py
```

---

**Built with ❤️ using LangChain, FastAPI, and OpenAI**
