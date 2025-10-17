Title: CS411 Data Dashboard

Purpose:
--------
The CS411 Data Dashboard is a comprehensive web-based application designed to explore and analyze academic research data across multiple database systems. The application serves as a demonstration platform for database management systems, showcasing the integration of three different database technologies: MySQL (relational), Neo4j (graph), and MongoDB (document).

Target Users:
- Database students and researchers learning about different database paradigms
- Academic administrators seeking insights into faculty research activities
- Data analysts exploring publication patterns and keyword relationships
- Educators demonstrating database concepts and implementations

Objectives:
- Demonstrate multi-database architecture and integration
- Provide interactive data exploration capabilities
- Showcase different query patterns and optimization techniques
- Enable users to search, filter, and save academic publication data
- Visualize research trends and faculty expertise areas

Demo:
-----
Video Demo: https://mediaspace.illinois.edu/media/t/1_caiv5ch8

Installation:
------------
1. Prerequisites:
   - Python 3.8 or higher
   - MySQL Server (for academicworld database)
   - Neo4j Database (for graph queries)
   - MongoDB Server (for document storage)

2. Clone or download the project files to your local machine

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure database connections:
   - Copy config.env.example to config.env (if available)
   - Update config.env with your database credentials:

5. Ensure all three databases are running and accessible

6. Run the application:
   ```
   python app.py
   ```

7. Open your web browser and navigate to http://localhost:8050

Usage:
------
1. University Faculty Directory:
   - Select a university from the dropdown
   - Choose sample size (10, 20, 30, 50, 100, or All)
   - Click "Generate New Sample" for different random samples
   - View faculty details including name, position, research interests, and publication counts

2. Publication Search by Keyword:
   - Enter a keyword in the search box
   - Select sample size and year range filters
   - Click "Search" to find relevant publications
   - Use checkboxes to select specific publications
   - Click "Save Selected to MongoDB" to store results
   - Add optional notes for saved searches

3. Faculty Publication Search:
   - Enter a faculty member's name
   - Apply filters for sample size and year range
   - View detailed publication information
   - Save selected publications to MongoDB

4. Top Keywords by Institute (Neo4j):
   - Select an institute from the dropdown
   - View interactive pie chart of top keywords
   - Analyze keyword distribution and relevance scores

5. Top Faculty by Citations (Neo4j):
   - View automatically generated chart of top faculty
   - See total citations and faculty count statistics
   - Analyze citation patterns across institutions

6. Saved Publications Data (MongoDB):
   - View all saved searches with metadata
   - Click "View" to see detailed publication lists
   - Click "Delete" to remove saved searches
   - Refresh data to see latest changes

Design:
-------
Overall Architecture:
The application follows a modular, multi-tier architecture:

Frontend Layer:
- Dash (Plotly) web framework for interactive UI
- Bootstrap components for responsive design
- Interactive charts and data tables
- Real-time data filtering and sampling

Application Layer:
- Python-based business logic
- Callback-driven interactivity
- Data processing and transformation
- Multi-database query coordination

Database Layer:
- MySQL: Primary relational data storage
- Neo4j: Graph-based relationship analysis
- MongoDB: Document storage for saved searches

Components:
1. University Faculty Widget: Displays faculty information with sampling capabilities
2. Publication Search Widget: Keyword-based search with filtering
3. Faculty Publication Widget: Faculty-specific publication search
4. Top Keywords Widget: Neo4j-powered keyword analysis
5. Top Faculty Widget: Citation-based faculty ranking
6. Saved Data Widget: MongoDB-based data persistence

Key Design Principles:
- Responsive design for various screen sizes
- Modular component architecture
- Separation of concerns between UI and data layers
- Error handling and user feedback
- Data sampling for performance optimization

Implementation:
--------------
Frameworks and Libraries:

Web Framework:
- Dash 2.14.2: Interactive web application framework
- Dash Bootstrap Components 1.5.0: UI component library
- Plotly 5.17.0: Interactive data visualization

Database Connectors:
- mysql-connector-python 8.2.0: MySQL database connectivity
- neo4j 5.15.0: Neo4j graph database driver
- pymongo 4.6.1: MongoDB document database driver

Data Processing:
- pandas 2.1.4: Data manipulation and analysis
- python-dotenv 1.0.0: Environment variable management

Tools and Technologies:
- Python 3.8+: Core programming language
- SQL: Relational database queries
- Cypher: Neo4j graph query language
- MongoDB Query Language: Document database operations
- HTML/CSS/JavaScript: Frontend rendering (via Dash)

Implementation Features:
1. Multi-Database Integration:
   - Unified connection management
   - Error handling and retry mechanisms
   - Connection pooling and optimization

2. Interactive Data Visualization:
   - Pie charts for keyword and citation analysis
   - Responsive data tables with sorting
   - Real-time data updates

3. Advanced Search Capabilities:
   - Keyword-based publication search
   - Faculty name search with fuzzy matching
   - Year range filtering
   - Sample size selection

4. Data Persistence:
   - MongoDB document storage for saved searches
   - Metadata tracking (timestamps, notes)
   - CRUD operations for saved data

5. Performance Optimization:
   - Data sampling for large result sets
   - Efficient database queries with indexing
   - Connection pooling and caching

Database Techniques:
-------------------
1. MySQL (Relational Database):
   - Normalized schema design with foreign key constraints
   - Complex JOIN operations for faculty-publication relationships
   - Aggregation queries for publication counts and citation averages
   - Indexed fields for optimized search performance
   - Score-based relevance ranking in junction tables

2. Neo4j (Graph Database):
   - Graph-based relationship modeling
   - Complex path traversal queries
   - Score-weighted relationship analysis
   - Pattern matching for keyword-faculty connections

3. MongoDB (Document Database):
   - Flexible document schema for saved searches
   - Array-based storage for multiple authors/keywords
   - Embedded metadata and timestamps
   - Text search and aggregation pipelines

Advanced Database Techniques:
1. Multi-Database Transactions:
   - Coordinated data operations across different database types
   - Error handling and rollback mechanisms
   - Data consistency maintenance

2. Query Optimization:
   - Indexed fields for fast search operations
   - Efficient JOIN strategies in MySQL
   - Graph traversal optimization in Neo4j
   - Aggregation pipeline optimization in MongoDB

3. Data Sampling:
   - Random sampling for large datasets
   - Configurable sample sizes
   - Performance vs. accuracy trade-offs

4. Real-time Data Processing:
   - Live database queries
   - Dynamic result updates
   - Interactive filtering and sorting

5. Data Visualization Integration:
   - Direct database-to-chart data flow
   - Real-time chart updates
   - Interactive data exploration

The application demonstrates advanced database concepts including:
- Polyglot persistence (using multiple database types)
- Graph-based relationship analysis
- Document-based flexible storage
- Relational data integrity
- Performance optimization techniques
- Real-time data visualization
