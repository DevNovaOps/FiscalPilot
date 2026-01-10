-- Fiscal Pilot Database Creation Script
-- Run this in MySQL command line or MySQL Workbench

-- Create the database
CREATE DATABASE IF NOT EXISTS fiscal_pilot 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Use the database
USE fiscal_pilot;

-- (Optional) Create a dedicated user (replace 'your_password' with a secure password)
-- CREATE USER IF NOT EXISTS 'fiscal_user'@'localhost' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON fiscal_pilot.* TO 'fiscal_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Verify database was created
SHOW DATABASES LIKE 'fiscal_pilot';
