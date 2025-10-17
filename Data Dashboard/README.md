# Multi-Database Analytics Dashboard

A comprehensive data dashboard built with Dash that connects to MySQL, MongoDB, and Neo4j databases. The dashboard features 6 interactive widgets that can display data from all three database types.

## Features

- **Multi-Database Support**: Connect to MySQL, MongoDB, and Neo4j simultaneously
- **6 Interactive Widgets**: Each widget can query different databases
- **Real-time Updates**: Refresh button to update all widgets with fresh data
- **Connection Status**: Visual indicators showing database connection status
- **Error Handling**: Robust error handling for database connections and queries
- **Responsive Design**: Modern, responsive UI built with Dash

## Database Connection Setup

### Option 1: Environment Variables (Recommended)

Create a `.env` file in the project root with your database credentials:

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=your_database_name
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_AUTH_SOURCE=admin

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

### Option 2: Direct Configuration

Modify the connection parameters in `app.py` in the `initialize_database_connections()` function:

```python
# MySQL Connection
mysql_conn = MySQLConnection(
    host='localhost',           # CHANGE: Your MySQL host
    port=3306,                  # CHANGE: Your MySQL port
    database='academicworld',   # CHANGE: Your MySQL database name
    user='root',       # CHANGE: Your MySQL username
    password='Green@7030'    # CHANGE: Your MySQL password
)

# MongoDB Connection
mongodb_conn = MongoDBConnection(
    host='localhost',           # CHANGE: Your MongoDB host
    port=27017,                 # CHANGE: Your MongoDB port
    database='admin',   # CHANGE: Your MongoDB database name
    username='root',   # CHANGE: Your MongoDB username (optional)
    password='Green7030'    # CHANGE: Your MongoDB password (optional)
)

# Neo4j Connection
neo4j_conn = Neo4jConnection(
    uri='bolt://localhost:7687',  # CHANGE: Your Neo4j URI
    username='neo4j',             # CHANGE: Your Neo4j username
    password='Green@7030',          # CHANGE: Your Neo4j password
    database='academicworld'              # CHANGE: Your Neo4j database name
)
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your database connections** (see above)

4. **Run the dashboard**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8050`

## Widget Implementation

The dashboard includes 6 placeholder widgets that you can customize with your specific queries:

### Widget 1: MySQL Data
- **Function**: `get_mysql_widget_data()`
- **Purpose**: Display data from MySQL database
- **Current**: Placeholder query `SELECT 1 as test`

### Widget 2: MongoDB Data  
- **Function**: `get_mongodb_widget_data()`
- **Purpose**: Display data from MongoDB database
- **Current**: Placeholder query to find documents in a collection

### Widget 3: Neo4j Data
- **Function**: `get_neo4j_widget_data()`
- **Purpose**: Display graph data from Neo4j database
- **Current**: Placeholder query `MATCH (n) RETURN count(n) as node_count`

### Widget 4: Combined Data
- **Function**: `get_combined_widget_data()`
- **Purpose**: Display data combining multiple databases
- **Current**: Placeholder - to be implemented

### Widget 5: Time Series
- **Function**: `get_timeseries_widget_data()`
- **Purpose**: Display time-series data
- **Current**: Placeholder - to be implemented

### Widget 6: Summary Statistics
- **Function**: `get_summary_widget_data()`
- **Purpose**: Display summary statistics
- **Current**: Placeholder - to be implemented

## Customizing Widgets

To implement your specific queries, modify the widget functions in `app.py`:

```python
def get_mysql_widget_data():
    """Get data for Widget 1 from MySQL"""
    try:
        if mysql_conn and mysql_conn.connection:
            # REPLACE WITH YOUR MYSQL QUERY
            query = "SELECT column1, column2 FROM your_table WHERE condition"
            results = mysql_conn.execute_query(query)
            
            if results:
                # Process your data and create visualization
                df = pd.DataFrame(results, columns=['column1', 'column2'])
                fig = px.bar(df, x='column1', y='column2', title="Your MySQL Data")
                info = f"Data from MySQL: {len(results)} records"
            else:
                fig = go.Figure().add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
                info = "No data available from MySQL"
        else:
            fig = go.Figure().add_annotation(text="MySQL not connected", x=0.5, y=0.5, showarrow=False)
            info = "MySQL connection not available"
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        info = f"Error accessing MySQL: {str(e)}"
    
    return fig, info
```

## Database Utilities

The project includes comprehensive utility classes for each database:

### MySQL Utilities (`mysql_utils.py`)
- Connection management
- Query execution (SELECT, INSERT, UPDATE, DELETE)
- Table information and metadata
- Batch operations

### MongoDB Utilities (`mongodb_utils.py`)
- Document operations (insert, find, update, delete)
- Collection management
- Aggregation support
- Index management

### Neo4j Utilities (`neo4j_utils.py`)
- Node and relationship operations
- Cypher query execution
- Graph traversal
- Index and constraint management

## Troubleshooting

### Connection Issues
1. **Check database services**: Ensure MySQL, MongoDB, and Neo4j are running
2. **Verify credentials**: Double-check usernames, passwords, and database names
3. **Check ports**: Ensure the correct ports are open and accessible
4. **Network connectivity**: Verify network connectivity to database servers

### Import Errors
1. **Install dependencies**: Run `pip install -r requirements.txt`
2. **Check Python environment**: Ensure you're using the correct Python environment
3. **Restart IDE**: Sometimes IDEs need to be restarted to recognize new packages

### Widget Errors
1. **Check database connections**: Ensure all databases are connected
2. **Verify queries**: Test your queries directly in the database clients
3. **Check data format**: Ensure your data can be converted to pandas DataFrames

## File Structure

```
├── app.py                 # Main Dash application
├── mysql_utils.py         # MySQL connection utilities
├── mongodb_utils.py       # MongoDB connection utilities
├── neo4j_utils.py         # Neo4j connection utilities
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .env                  # Environment variables (create this)
```

## Next Steps

1. **Set up your database connections** using environment variables or direct configuration
2. **Implement your specific queries** in the widget functions
3. **Customize visualizations** using Plotly Express or Graph Objects
4. **Add interactive features** like filters, date ranges, or dropdowns
5. **Deploy to production** using a WSGI server like Gunicorn

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your database connections are working
3. Test your queries directly in the database clients
4. Check the console output for error messages
