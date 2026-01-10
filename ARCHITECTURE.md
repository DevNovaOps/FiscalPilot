# Fiscal Pilot - System Architecture

## Overview

Fiscal Pilot is an agent-first, explainable financial intelligence platform built with Flask, LangGraph, and modern web technologies. The system uses multiple AI agents orchestrated by LangGraph to provide transparent, educational financial guidance.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  HTML/CSS/JavaScript (Vanilla) - Cyberpunk Styled           │
│  - Landing, Dashboard, Expenses, Insights, Risk Profile     │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                      Flask Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Auth API    │  │ Transaction  │  │  Analysis    │     │
│  │              │  │     API      │  │     API      │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
│                                               │              │
│                          ┌────────────────────▼────────────┐│
│                          │   Agent Orchestrator            ││
│                          │   (LangGraph)                   ││
│                          └──────────┬──────────────────────┘│
│                                     │                        │
┌─────────────────────────────────────▼────────────────────────┐
│                  LangGraph Agent Flow                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Transaction  │→ │   Behavior   │→ │ Investment   │      │
│  │  Intelligence│  │    Agent     │  │  Knowledge   │      │
│  └──────────────┘  └──────────────┘  └──────┬───────┘      │
│                                               │               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────▼───────┐      │
│  │   Decision   │→ │Explainability│← │  Compliance  │      │
│  │  Confidence  │  │    Agent     │  │   Guard      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
                       │
                       │ Groq API (LLM)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      MySQL Database                          │
│  - Users, Transactions, Risk Profiles, AI Decisions         │
└──────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend (Static HTML/CSS/JS)

**Location**: `frontend/`

**Key Files**:
- `index.html` - Landing page
- `dashboard.html` - Main dashboard
- `expenses.html` - Transaction management
- `insights.html` - AI analysis results
- `risk-profile.html` - Risk assessment display
- `education.html` - Investment education
- `settings.html` - User preferences

**Styling**:
- Cyberpunk theme with dark/light mode
- Glassmorphism effects
- Neon accents and glows
- Responsive mobile-first design

**JavaScript**:
- `app.js` - API client and utilities
- `theme.js` - Theme management

### 2. Backend (Flask)

**Location**: `backend/`

**Structure**:
```
backend/
├── app.py              # Flask application entry
├── config.py           # Configuration management
├── db.py               # Database initialization
├── api/                # REST API routes
│   ├── auth.py         # Authentication
│   ├── transactions.py # Transaction management
│   ├── analysis.py     # AI analysis endpoints
│   ├── preferences.py  # User preferences
│   └── mock.py         # Mock AA data
├── models/             # SQLAlchemy models
│   ├── user.py
│   ├── transaction.py
│   ├── risk_profile.py
│   ├── ai_decision.py
│   └── user_preference.py
├── schemas/            # Pydantic validation
└── agents/             # AI agents (see below)
```

### 3. AI Agent System (LangGraph)

**Location**: `backend/agents/`

**Agents**:

1. **Transaction Intelligence Agent** (`transaction_agent.py`)
   - Categorizes transactions
   - Detects EMI, subscriptions, discretionary spending
   - Identifies patterns

2. **Financial Behavior Agent** (`behavior_agent.py`)
   - Analyzes income stability
   - Measures expense volatility
   - Calculates risk tolerance score (0-100)

3. **Investment Knowledge Agent** (`investment_agent.py`)
   - Provides educational content about:
     - Stocks (risk tiers)
     - Gold (forms and characteristics)
     - Debt instruments (safe assets)
   - **No predictions, only educational information**

4. **Decision Confidence Agent** (`decision_agent.py`)
   - Combines behavior + risk + goals
   - Determines suitable/unsuitable options
   - Provides confidence scores

5. **Explainability Agent** (`explainability_agent.py`)
   - Explains WHY decisions were made
   - Shows risks and worst-case scenarios
   - Makes reasoning transparent

6. **Compliance Guard Agent** (`compliance_agent.py`)
   - Validates all outputs
   - Ensures educational (not advisory) tone
   - Blocks unsafe responses
   - Runs in parallel on all agent outputs

**Orchestration** (`orchestrator.py`):
- Uses LangGraph to coordinate agents
- Maintains state through agent flow
- Logs all decisions for auditability

### 4. Database (MySQL)

**Models**:

- `User` - User accounts and preferences
- `Transaction` - Financial transactions
- `RiskProfile` - AI-generated risk assessment
- `AIDecision` - Logged AI decisions (for audit)
- `UserPreference` - User goals and preferences

**Schema Design**:
- Relational design with foreign keys
- JSON fields for flexible data storage
- Timestamps for auditability
- Soft deletes via cascade

## Data Flow

### User Transaction Upload

1. User uploads CSV or uses mock AA data
2. Transactions stored in MySQL
3. Frontend displays transactions

### AI Analysis Flow

1. User requests analysis via `/api/analysis/full-analysis`
2. Agent Orchestrator initialized
3. LangGraph executes agent flow:
   ```
   Transactions → Transaction Agent
                ↓
   Behavior Agent (analyzes patterns)
                ↓
   Investment Knowledge Agent (gets education)
                ↓
   Decision Confidence Agent (makes decisions)
                ↓
   Explainability Agent (explains why)
                ↓
   Compliance Guard (validates output)
                ↓
   Final Output
   ```
4. Risk profile saved to database
5. AI decisions logged for audit
6. Results returned to frontend

### Risk Profile Generation

1. Behavior Agent analyzes:
   - Savings rate
   - Income stability
   - Expense volatility
   - Recurring obligations
   - Discretionary spending

2. Risk score calculated (0-100)
3. Risk level assigned (Low/Medium/High)
4. Explanation generated
5. Stored in `RiskProfile` table

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Create transaction
- `POST /api/transactions/upload-csv` - Upload CSV
- `DELETE /api/transactions/<id>` - Delete transaction

### Analysis
- `POST /api/analysis/full-analysis` - Run AI analysis
- `GET /api/analysis/risk-profile` - Get risk profile
- `GET /api/analysis/insights` - Get previous insights

### Preferences
- `GET /api/preferences` - Get preferences
- `PUT /api/preferences` - Update preferences

### Mock Data
- `GET /api/mock-aa/consent` - Get consent info
- `POST /api/mock-aa/import` - Import mock data

## Security & Compliance

### Authentication
- JWT tokens for session management
- Password hashing with werkzeug
- Token expiration (7 days)

### Data Privacy
- User consent required before data usage
- No data shared with third parties
- All AI decisions logged for audit

### Compliance
- Compliance Guard Agent validates outputs
- Educational-only language enforced
- No guarantees or predictions
- Clear disclaimers on all outputs
- Risk warnings included

## Technology Stack

### Backend
- **Flask** - Web framework (chosen for flexibility with agents)
- **SQLAlchemy** - ORM
- **MySQL** - Database
- **Pydantic** - Data validation
- **LangChain** - AI framework
- **LangGraph** - Agent orchestration
- **Groq API** - LLM inference

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Custom cyberpunk styling
- **HTML5** - Semantic markup

## Scalability Considerations

### Current Implementation
- Single Flask instance
- Direct MySQL connection
- In-memory agent execution

### Production Enhancements
- Use WSGI server (gunicorn, uwsgi)
- Database connection pooling
- Redis for caching
- Queue system for async agent execution
- Load balancer for multiple instances
- CDN for static assets

## Monitoring & Logging

### Current
- AI decisions logged in database
- Error handling in API endpoints
- Console logging

### Production
- Structured logging (e.g., structlog)
- Error tracking (Sentry)
- Performance monitoring (APM)
- Database query logging
- Agent execution metrics

## Testing Strategy

### Unit Tests
- Agent logic
- API endpoints
- Data models

### Integration Tests
- Agent orchestration
- Database operations
- API workflows

### E2E Tests
- User flows
- AI analysis pipelines

## Deployment

### Development
```bash
python run.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## Future Enhancements

1. **Real Account Aggregator Integration**
   - Replace mock data with real AA framework
   - OAuth-based authentication
   - Secure data fetching

2. **Advanced Agents**
   - Real-time transaction categorization
   - Predictive insights (with disclaimers)
   - Goal tracking agent

3. **Enhanced Frontend**
   - Real-time updates (WebSockets)
   - Advanced visualizations
   - Mobile app

4. **Analytics**
   - User behavior tracking
   - Agent performance metrics
   - Decision accuracy tracking

## Notes

- All AI outputs are educational, not advisory
- No guarantees are made about returns
- Past performance ≠ future results
- User should consult financial advisors for investment decisions
- System is designed for transparency and explainability
