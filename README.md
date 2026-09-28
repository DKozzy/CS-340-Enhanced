# CS-340 Enhanced Grazioso Salvare Dashboard

This repository contains the enhanced version of my CS-340 Grazioso Salvare project, completed as part of my CS-499 Computer Science Capstone at Southern New Hampshire University.

The original project was developed as a Python and MongoDB client/server application for managing and analyzing animal shelter data. It included a reusable CRUD module and an interactive Dash dashboard that allowed rescue organizations to filter shelter records and identify animals that may be suitable for different types of rescue work.

For my capstone, I expanded the database layer and dashboard to improve database efficiency, scalability, data integrity, security, and analytical capabilities.

## About the Original Project

The original Grazioso Salvare application was developed using Python, MongoDB, PyMongo, Dash, Plotly, and Dash Leaflet.

The project consisted of a reusable MongoDB CRUD module and an interactive dashboard. The CRUD module provided database operations for animal shelter records, while the dashboard allowed users to filter records, view animal information in a table, visualize breed information, and display the selected animal's location on a map.

## Capstone Enhancement

For the Databases category of my CS-499 ePortfolio, I enhanced the project by expanding the MongoDB data-access layer and improving how the dashboard retrieves, validates, analyzes, and displays shelter data.

Major enhancements include:

- Added server-side pagination for MongoDB records
- Added database-level sorting
- Added document-counting functionality
- Added MongoDB aggregation pipelines for breed analysis
- Added compound indexing for commonly queried rescue fields
- Added query execution analysis using MongoDB explain statistics
- Added database performance testing comparing indexed queries with collection scans
- Added document normalization and validation
- Added validation and normalization for database updates
- Improved database error handling
- Removed hardcoded database passwords and introduced environment-based credential management
- Added server-side Dash pagination and sorting
- Centralized rescue-filter query construction
- Updated dashboard visualizations to use database aggregation results
- Preserved existing CRUD functionality while extending the database layer

## Database Optimization

The enhanced application uses MongoDB indexes to improve the efficiency of rescue-related queries. A compound index was created using fields commonly involved in rescue filtering, including animal type, breed, sex upon outcome, and age upon outcome in weeks.

Query performance was evaluated using MongoDB execution statistics. During testing, the indexed rescue query returned 17 matching documents while examining only 17 documents and 22 index keys. A forced collection scan returned the same 17 records but examined all 10,000 documents in the dataset.

This represented approximately a 99.83% reduction in documents examined and demonstrated the impact that appropriate indexing can have on database query efficiency.

## Aggregation and Data Retrieval

MongoDB aggregation was added to perform breed analysis directly within the database rather than requiring the dashboard to retrieve and process the entire dataset.

The enhanced data-access layer also supports pagination, sorting, and document counting. These features allow the dashboard to request only the records needed for the current page rather than loading thousands of records into memory at once.

The dashboard uses these capabilities to provide server-side pagination and sorting while maintaining the rescue filtering functionality of the original application.

## Data Integrity and Security

Document normalization and validation were introduced to improve the consistency of data entering the database. Text values are normalized before storage, required fields are validated, and invalid values such as negative animal ages are rejected.

These checks are applied to both new records and updates to existing records.

The database connection was also improved by removing the hardcoded MongoDB password from the source code. The enhanced application retrieves the database password from the `AAC_MONGO_PASSWORD` environment variable and uses authenticated MongoDB connections.

## Testing and Performance Analysis

The enhanced project includes a comprehensive testing script that verifies:

- Database connectivity
- Pagination behavior
- Aggregation pipelines
- Index creation and usage
- Indexed query performance
- Document normalization
- Document validation
- Create operations
- Update operations
- Invalid data rejection

Testing confirmed that the enhanced database functionality operates correctly while preserving the existing behavior of the application.

## Technologies

- Python
- MongoDB
- PyMongo
- Dash
- Plotly
- Dash Leaflet
- Jupyter Notebook

## Skills Demonstrated

This enhancement demonstrates skills in:

- Database design and development
- MongoDB CRUD operations
- Query optimization
- Database indexing
- Aggregation pipelines
- Server-side pagination and sorting
- Query performance analysis
- Data validation and normalization
- Secure credential management
- Client/server architecture
- Python application development
- Database-driven data visualization
- Software testing and error handling

## CS-499 ePortfolio

This project represents the **Databases** enhancement for my CS-499 Computer Science Capstone ePortfolio.

The enhancement demonstrates my ability to move beyond basic CRUD operations and consider how database-backed applications handle performance, scalability, data integrity, security, and analytical processing. The enhanced database layer works together with the Dash interface to provide more efficient access to the shelter dataset while maintaining the functionality of the original application.
