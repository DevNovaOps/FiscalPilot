# Database Setup Guide

## Step 1: Create MySQL Database

### Option A: Using MySQL Command Line

1. Open MySQL command line or MySQL Workbench
2. Login as root or admin user:
```bash
mysql -u root -p
```

3. Run these SQL commands:
```sql
-- Create the database
CREATE DATABASE fiscal_pilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- (Optional) Create a dedicated user
CREATE USER 'fiscal_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON fiscal_pilot.* TO 'fiscal_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify database was created
SHOW DATABASES;
```

4. Exit MySQL:
```sql
EXIT;
```

### Option B: Using MySQL Workbench (GUI)

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Run this query:
```sql
CREATE DATABASE fiscal_pilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
4. Click the Execute button (⚡)

## Step 2: Configure .env File

Create a `.env` file in the project root directory (`C:\FicsalPilot\.env`)

The database connection is configured in: **`.env` file**

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=fiscal_pilot
```

**Important:**
- `DB_HOST`: Usually `localhost` for local MySQL
- `DB_PORT`: Default is `3306`
- `DB_USER`: Your MySQL username (usually `root` for local)
- `DB_PASSWORD`: Your MySQL password
- `DB_NAME`: The database name (`fiscal_pilot`)

## Step 3: Verify Connection

After creating the `.env` file, run:

```bash
python init_db.py
```

This will:
- Connect to your database
- Create all necessary tables
- Verify the connection works

## Troubleshooting

**Can't connect to MySQL?**
- Make sure MySQL service is running
- Check MySQL is installed: `mysql --version`
- Verify credentials in `.env` file

**Access denied?**
- Check username and password
- Make sure user has privileges on the database

**Database doesn't exist?**
- Run Step 1 again to create the database
- Check database name matches in `.env`
