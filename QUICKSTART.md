# Fiscal Pilot - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### Step 2: Set Up Database

1. Start MySQL
2. Create database:
```sql
CREATE DATABASE fiscal_pilot;
```

3. Update `.env` file with your MySQL credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=fiscal_pilot
GROQ_API_KEY=your_groq_api_key
```

### Step 3: Get Groq API Key

1. Go to https://console.groq.com
2. Sign up/Login
3. Create API key
4. Add to `.env` file

### Step 4: Initialize Database

```bash
python init_db.py
```

### Step 5: Run the Application

```bash
python run.py
```

Visit: http://localhost:5000

## 📝 First Steps

1. **Register** - Create your account
2. **Add Transactions** - Either:
   - Upload `sample_transactions.csv` 
   - Or add transactions manually
   - Or use mock Account Aggregator data
3. **Run Analysis** - Go to "AI Insights" → Click "Run Full Analysis"
4. **View Results** - Check Risk Profile and Insights

## 🎯 Key Features to Try

- **Dashboard** - Overview of your finances
- **Expenses** - View and manage transactions
- **AI Insights** - Run comprehensive analysis
- **Risk Profile** - See your risk assessment
- **Education** - Learn about investments
- **Settings** - Configure preferences

## 🔍 Understanding the Output

### Risk Profile
- **Low (0-35)**: Stable finances, low risk tolerance
- **Medium (36-65)**: Moderate stability and risk
- **High (66-100)**: High volatility, aggressive risk

### Investment Suitability
- **Suitable**: Matches your risk profile
- **Moderately Suitable**: Some alignment with risk
- **Unsuitable**: Doesn't match your profile

### Explanations
Every decision includes:
- Why it was made
- What factors influenced it
- What the risks are
- Worst-case scenarios

## ⚠️ Important Notes

- **Educational Only**: All guidance is educational, not investment advice
- **No Guarantees**: No predictions or guarantees about returns
- **Consult Advisors**: Always consult certified financial advisors
- **Risk Awareness**: All investments carry risk

## 🐛 Troubleshooting

**Database connection error?**
- Check MySQL is running
- Verify credentials in `.env`

**Groq API error?**
- Check API key is correct
- Verify internet connection
- Check API quota

**Import errors?**
- Ensure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

## 📚 Next Steps

- Read `SETUP.md` for detailed setup
- Check `ARCHITECTURE.md` for system design
- Explore the codebase
- Customize for your needs

## 💡 Tips

- Start with sample CSV to see how it works
- Run analysis after adding 20+ transactions
- Review explanations to understand AI reasoning
- Adjust preferences in Settings for personalized insights

---

**Ready to pilot your finances?** 🚀
