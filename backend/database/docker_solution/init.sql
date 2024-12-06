/*
Database for the Coffee Time Web Application
-----

Provides team_members and users for login

*/

CREATE DATABASE IF NOT EXISTS coffee_db;
CREATE USER IF NOT EXISTS 'coffee_user'@'%' IDENTIFIED BY 'coffeeaddict';
GRANT ALL PRIVILEGES ON coffee_db.* TO 'coffee_user'@'%';
FLUSH PRIVILEGES;

USE coffee_db;

CREATE TABLE IF NOT EXISTS team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    times_paid INT DEFAULT 0,
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
