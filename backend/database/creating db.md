sudo mysql -u root -p

CREATE USER 'coffee_user'@'localhost' IDENTIFIED BY 'coffeeaddict';

CREATE DATABASE coffee_db;

GRANT ALL PRIVILEGES ON coffee_db.* TO 'coffee_user'@'localhost';

FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    times_paid INT DEFAULT 0,
);

EXIT;
