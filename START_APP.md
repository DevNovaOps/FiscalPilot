# How to Start Fiscal Pilot

## Quick Start

### Option 1: Run Without Database (For Testing Frontend)

If you just want to test the frontend without database setup:

```bash
python run.py
```

The app will start on `http://localhost:5000`. Note: API endpoints that require database will fail until database is configured.

### Option 2: Full Setup (Recommended)

#### Step 1: Configure Database

1. Make sure MySQL is running
2. Create the database:
   ```sql
   CREATE DATABASE fiscal_pilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. Update `.env` file with your MySQL credentials:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=fiscal_pilot
   ```

#### Step 2: Initialize Database

```bash
python init_db.py
```

This will create all necessary tables in your database.

#### Step 3: Start the Application

```bash
python run.py
```

Visit: http://localhost:5000

---

## Troubleshooting

### "Can't connect to MySQL server"

- Check MySQL is running: `mysql --version`
- Verify credentials in `.env` file
- Make sure database `fiscal_pilot` exists
- Try connecting manually: `mysql -u root -p`

### "Module not found" errors

Make sure you're in the virtual environment:
```bash
venv\Scripts\activate  # Windows
```

And all dependencies are installed:
```bash
pip install -r requirements.txt
```

### App starts but API endpoints fail

- Database tables might not be created
- Run: `python init_db.py`
- Check `.env` has correct database credentials

---

## Environment Variables

Required in `.env`:

```env
# Database (Required for full functionality)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=fiscal_pilot

# Groq API (Required for AI agents)
GROQ_API_KEY=your_groq_api_key

# Flask (Can use defaults)
SECRET_KEY=your-secret-key
DEBUG=True
PORT=5000
```
