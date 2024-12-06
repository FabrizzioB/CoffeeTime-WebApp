# Use the official MySQL image from the Docker Hub
FROM mysql:8.0.32

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=coffee_db
ENV MYSQL_USER=coffee_addict
ENV MYSQL_PASSWORD=coffeelove

# Expose the default MySQL port
EXPOSE 3306

# Run the MySQL server when the container starts
CMD ["mysqld"]

# Copy starting SQL script to the starting directory of MySQL.
COPY init.sql /docker-entrypoint-initdb.d/
