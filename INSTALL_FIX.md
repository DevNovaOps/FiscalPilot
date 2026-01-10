# Installation Fix for Windows

The installation is failing because `pydantic-core` needs to compile Rust code. Here are solutions:

## Solution 1: Install with Pre-built Wheels Only (Recommended)

Run these commands in order:

```bash
# Install pydantic with pre-built wheels only (no compilation)
pip install --only-binary :all: pydantic pydantic-settings

# Then install the rest (they should use the already-installed pydantic)
pip install -r requirements.txt
```

## Solution 2: Install Rust Properly

If Solution 1 doesn't work, install Rust:

1. Download and install Rust from: https://rustup.rs/
2. Or install via: `winget install Rustlang.Rust.MSVC`
3. After installation, restart your terminal
4. Then run: `pip install -r requirements.txt`

## Solution 3: Use Python 3.11 or 3.12 Instead

Python 3.13 is very new and may not have pre-built wheels for all packages. Consider using Python 3.11 or 3.12 which have better wheel availability.

## Solution 4: Manual Installation Order

Try installing packages in this specific order:

```bash
pip install --only-binary :all: pydantic-core
pip install pydantic pydantic-settings
pip install Flask Flask-CORS Flask-SQLAlchemy
pip install PyMySQL mysql-connector-python cryptography
pip install SQLAlchemy
pip install python-dotenv python-dateutil
pip install bcrypt PyJWT
pip install langchain langchain-groq langgraph langchain-community
```

## Quick Fix Script

Run this in PowerShell:

```powershell
pip install --only-binary :all: pydantic pydantic-settings
pip install -r requirements.txt
```
