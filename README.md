Overview
This project implements a log ingestion and query interface capable of handling large volumes of log data. It uses a combination of Flask (Python), Elasticsearch, and PostgreSQL to provide efficient data handling and querying capabilities.

Setup Instructions
Install Dependencies:
Ensure Python, Elasticsearch, and PostgreSQL are installed.
Install required Python libraries: Flask, psycopg2, elasticsearch, etc.
Database Setup:
Set up Elasticsearch and PostgreSQL databases.
Create the necessary indices and tables.
Running the Application:
Start the Elasticsearch and PostgreSQL services.
Run the Flask application: python app.py.
System Design
Log Ingestor: A Flask-based HTTP server that ingests log data and stores it in Elasticsearch and PostgreSQL.
Query Interface: Provides an interface to query the ingested logs with options like full-text search, and filters based on various log fields.
Elasticsearch: Handles full-text search and quick retrieval of logs.
PostgreSQL: Manages structured data and enables complex SQL queries.
Features
HTTP Log Ingestion: Efficient ingestion of logs over HTTP.
Scalable Architecture: Both Elasticsearch and PostgreSQL offer scalability for handling large data volumes.
Full-Text Search: Elasticsearch powers the full-text search capabilities.
Field-Based Filters: Queries can be filtered based on specific log fields.
Web-based Query Interface: A user-friendly web interface for querying logs.
