# Fiscal Pilot - Setup Guide

## Prerequisites

1. **Python 3.9+** - Check with `python --version`
2. **MySQL 8.0+** - Install MySQL Server
3. **Git** (optional) - For version control

## Installation Steps

### 1. Clone or Navigate to Project Directory
```bash
cd C:\FicsalPilot
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

1. Start MySQL service
2. Create database:
```sql
CREATE DATABASE fiscal_pilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Create a user (optional, or use root):
```sql
CREATE USER 'fiscal_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON fiscal_pilot.* TO 'fiscal_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production-use-random-string

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=fiscal_pilot

# Groq API Configuration
GROQ_API_KEY=your-groq-api-key-here

# Application Settings
DEBUG=True
PORT=5000
```

**To get a Groq API Key:**
1. Visit https://console.groq.com
2. Sign up/Login
3. Create an API key
4. Copy the key to your `.env` file

### 6. Initialize Database

```bash
python init_db.py
```

This will create all necessary tables in your MySQL database.

### 7. Run the Application

```bash
python run.py
```

Or:

```bash
python -m backend.app
```

The server will start on `http://localhost:5000`

## Project Structure

```
FiscalPilot/
├── backend/              # Flask backend
│   ├── agents/          # LangGraph agents
│   ├── api/             # REST API routes
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   └── app.py           # Flask app
├── frontend/            # Frontend files
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript
│   └── *.html          # HTML pages
├── requirements.txt     # Python dependencies
└── .env                # Environment variables (create this)
```

## Usage

1. **Visit the Application**: http://localhost:5000
2. **Register**: Create a new account
3. **Add Transactions**: 
   - Manually add transactions
   - Or upload a CSV file
4. **Run AI Analysis**: Go to AI Insights page and click "Run Full Analysis"
5. **View Results**: 
   - Risk Profile
   - Investment Suitability
   - Explanations

## CSV Upload Format

Your CSV file should have the following columns:
- `date` or `transaction_date` - Date in YYYY-MM-DD or DD/MM/YYYY format
- `amount` - Transaction amount (positive for income, negative for expenses)
- `description` - Transaction description
- `type` - Transaction type: income, expense, or transfer (optional)
- `category` - Transaction category (optional)
- `merchant` - Merchant name (optional)

Example:
```csv
date,amount,description,type,category
2024-01-15,-1500.00,Grocery Shopping,expense,Food & Dining
2024-01-20,50000.00,Salary,income,Salary
```

## Troubleshooting

### Database Connection Issues
- Check MySQL is running: `mysql -u root -p`
- Verify database credentials in `.env`
- Ensure database exists: `SHOW DATABASES;`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Groq API Issues
- Verify API key is correct in `.env`
- Check API quota at https://console.groq.com
- Ensure internet connection is available

### Port Already in Use
- Change `PORT` in `.env` to a different port (e.g., 5001)
- Or stop the process using port 5000

## Production Deployment

For production:
1. Set `DEBUG=False` in `.env`
2. Use a strong `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
3. Use a production WSGI server (gunicorn, uwsgi)
4. Set up proper database backups
5. Configure HTTPS
6. Set up proper logging
7. Review security settings

## Notes

- **Mock Data**: Currently uses mock Account Aggregator data and CSV upload
- **Production Ready**: Can integrate with real AA framework or Plaid
- **AI Agents**: All agents use Groq API for LLM inference
- **Compliance**: Built-in compliance checks ensure educational-only output

## Support

For issues or questions, refer to the README.md or check the code comments for detailed explanations.
