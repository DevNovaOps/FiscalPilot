# Fiscal Pilot 🚀
**An Agent-First, Explainable Financial Intelligence Platform**

Fiscal Pilot is a next-generation financial web application that uses agentic AI to provide transparent, educational financial guidance without making investment predictions or guarantees.

## 🎯 Core Philosophy

*"An AI financial co-pilot that explains decisions, not a budgeting app."*

## 🏗️ Architecture

### Tech Stack
- **Backend**: Flask (chosen for lightweight, flexible agent integration)
- **Database**: MySQL
- **AI Framework**: LangChain + LangGraph
- **LLM**: Groq API
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Validation**: Pydantic

### Agent Architecture

The system uses LangGraph to orchestrate 6 specialized agents:

1. **Transaction Intelligence Agent** - Categorizes and analyzes transactions
2. **Financial Behavior Agent** - Assesses risk tolerance and spending patterns
3. **Investment Knowledge Agent** - Provides educational content on assets
4. **Decision Confidence Agent** - Determines suitable financial options
5. **Explainability Agent** - Transparently explains all decisions
6. **Compliance Guard Agent** - Ensures educational, non-advisory output

## 🔒 Privacy & Compliance

- ✅ User consent required before data usage
- ✅ No direct bank/UPI access
- ✅ Mock Account Aggregator support
- ✅ CSV upload option
- ✅ All AI decisions logged for audit
- ✅ No guaranteed returns or direct investment advice

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MySQL 8.0+
- Node.js (for asset bundling, optional)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your MySQL and Groq API credentials

# Initialize database
python init_db.py

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser.

## 📁 Project Structure

```
FiscalPilot/
├── backend/
│   ├── app.py                 # Flask application entry
│   ├── config.py              # Configuration
│   ├── models/                # Database models
│   ├── schemas/               # Pydantic schemas
│   ├── agents/                # LangGraph agents
│   ├── api/                   # REST API routes
│   └── utils/                 # Utilities
├── frontend/
│   ├── index.html             # Landing page
│   ├── dashboard.html         # Main dashboard
│   ├── css/
│   │   ├── main.css           # Main styles
│   │   └── themes.css         # Theme definitions
│   └── js/
│       ├── app.js             # Main application logic
│       └── theme.js           # Theme switcher
├── static/                    # Static assets
├── templates/                 # Jinja2 templates (if needed)
└── tests/                     # Test suite
```

## 🎨 Design System

- **Theme**: Cyberpunk/Neon aesthetic
- **Colors**: Neon blues, purples, cyans with dark backgrounds
- **Effects**: Glassmorphism, subtle animations
- **Responsive**: Mobile-first design

## 📝 Development Notes

### Mock vs Production

- **Current Implementation**: Mock Account Aggregator JSON, CSV upload
- **Production Ready**: Integrate with real AA framework, Plaid (international), OAuth

### Data Flow

1. User uploads transaction data (CSV/JSON)
2. Data stored in MySQL
3. LangGraph orchestrates agents
4. Agents analyze and explain
5. UI displays insights with explainability

## 🤝 Contributing

This is a hackathon-ready project. Ensure all compliance checks pass before deployment.

## 📄 License

MIT License - See LICENSE file
