@echo off
REM Install pydantic with pre-built wheels only (no compilation)
pip install --only-binary :all: pydantic pydantic-settings

REM Now install the rest
pip install -r requirements.txt
