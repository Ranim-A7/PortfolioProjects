import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime, timedelta
import logging

# Database utilities
from mysql_utils import MySQLConnection, create_connection_from_env as create_mysql_connection
from mongodb_utils import MongoDBConnection, create_connection_from_env as create_mongodb_connection
from neo4j_utils import Neo4jConnection, create_connection_from_env as create_neo4j_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, title="Multi-Database Dashboard")
app.config.suppress_callback_exceptions = True

# Database connections
mysql_conn = None
mongodb_conn = None
neo4j_conn = None

def initialize_database_connections():
    """Initialize connections to all databases"""
    global mysql_conn, mongodb_conn, neo4j_conn
    
    # ========================================
    # DATABASE CONNECTION SETUP
    # ========================================
    
    # MySQL Connection
    # Set these environment variables or modify the connection parameters below:
    # MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
    try:
        mysql_conn = create_mysql_connection()
        if not mysql_conn:
            # Fallback to direct connection - MODIFY THESE PARAMETERS
            mysql_conn = MySQLConnection(
                host='localhost',  # CHANGE: Your MySQL host
                port=3306,         # CHANGE: Your MySQL port
                database='academicworld',  # CHANGE: Your MySQL database name
                user='root',      # CHANGE: Your MySQL username
                password='Green@7030'   # CHANGE: Your MySQL password
            )
        if mysql_conn.connect():
            logger.info("MySQL connection established")
        else:
            logger.error("Failed to connect to MySQL")
    except Exception as e:
        logger.error(f"MySQL connection error: {e}")
    
    # MongoDB Connection
    # Set these environment variables or modify the connection parameters below:
    # MONGODB_HOST, MONGODB_PORT, MONGODB_DATABASE, MONGODB_USERNAME, MONGODB_PASSWORD
    try:
        mongodb_conn = create_mongodb_connection()
        if not mongodb_conn:
            # Fallback to direct connection - MODIFY THESE PARAMETERS
            mongodb_conn = MongoDBConnection(
                host='localhost',      # CHANGE: Your MongoDB host
                port=27017,           # CHANGE: Your MongoDB port
                database='admin',  # CHANGE: Your MongoDB database name
                username='root',  # CHANGE: Your MongoDB username (optional)
                password='Green7030'   # CHANGE: Your MongoDB password (optional)
            )
        if mongodb_conn.connect():
            logger.info("MongoDB connection established")
        else:
            logger.error("Failed to connect to MongoDB")
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
    
    # Neo4j Connection
    # Set these environment variables or modify the connection parameters below:
    # NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
    try:
        neo4j_conn = create_neo4j_connection()
        if not neo4j_conn:
            # Fallback to direct connection - MODIFY THESE PARAMETERS
            neo4j_conn = Neo4jConnection(
                uri='bolt://localhost:7687',  # CHANGE: Your Neo4j URI
                username='neo4j',             # CHANGE: Your Neo4j username
                password='Green@7030',          # CHANGE: Your Neo4j password
                database='academicworld'              # CHANGE: Your Neo4j database name
            )
        if neo4j_conn.connect():
            logger.info("Neo4j connection established")
        else:
            logger.error("Failed to connect to Neo4j")
    except Exception as e:
        logger.error(f"Neo4j connection error: {e}")

# Initialize connections when app starts
initialize_database_connections()

# Dashboard layout
app.layout = html.Div([
    # Header
    html.H1("Multi-Database Analytics Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Database Status
    html.Div([
        html.H3("Database Connection Status", style={'color': '#34495e'}),
        html.Div([
            html.Span("MySQL: ", style={'fontWeight': 'bold'}),
            html.Span("Connected" if mysql_conn and mysql_conn.connection else "Disconnected", 
                     style={'color': 'green' if mysql_conn and mysql_conn.connection else 'red'}),
            html.Br(),
            html.Span("MongoDB: ", style={'fontWeight': 'bold'}),
            html.Span("Connected" if mongodb_conn and mongodb_conn.client else "Disconnected",
                     style={'color': 'green' if mongodb_conn and mongodb_conn.client else 'red'}),
            html.Br(),
            html.Span("Neo4j: ", style={'fontWeight': 'bold'}),
            html.Span("Connected" if neo4j_conn and neo4j_conn.driver else "Disconnected",
                     style={'color': 'green' if neo4j_conn and neo4j_conn.driver else 'red'})
        ], style={'marginBottom': 20})
    ], style={'backgroundColor': '#ecf0f1', 'padding': 15, 'borderRadius': 5, 'marginBottom': 20}),
    
    # Widget Grid
    html.Div([
        # Row 1
        html.Div([
            # Widget 1 - Publication Keyword Search
            html.Div([
                html.H4("Widget 1 - Publication Keyword Search", style={'textAlign': 'center'}),
                html.Div([
                    html.Label("Enter Keyword:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                    dcc.Input(
                        id='keyword-input',
                        type='text',
                        placeholder='Enter a keyword (e.g., machine learning, database, AI)...',
                        style={'width': '100%', 'padding': '8px', 'marginBottom': 10, 'border': '1px solid #ddd', 'borderRadius': '4px'}
                    ),
                    html.Button(
                        'Search Publications',
                        id='keyword-search-button',
                        n_clicks=0,
                        style={'backgroundColor': '#3498db', 'color': 'white', 'padding': '8px 16px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'marginRight': '10px'}
                    ),
                    html.Button(
                        'Show All Publications',
                        id='show-all-button',
                        n_clicks=0,
                        style={'backgroundColor': '#95a5a6', 'color': 'white', 'padding': '8px 16px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
                    )
                ], style={'marginBottom': 15}),
                dcc.Graph(id='widget-1-graph'),
                html.Div(id='widget-1-info', style={'textAlign': 'center', 'marginTop': 10})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': 10}),
            
            # Widget 2 - Keyword Comparison
            html.Div([
                html.H4("Widget 2 - Keyword Comparison", style={'textAlign': 'center'}),
                html.Div([
                    html.Label("Enter 5 Keywords to Compare:", style={'fontWeight': 'bold', 'marginBottom': 10}),
                    html.Div([
                        dcc.Input(
                            id='keyword-1-input',
                            type='text',
                            placeholder='Keyword 1 (e.g., machine learning)',
                            style={'width': '48%', 'padding': '6px', 'marginRight': '2%', 'border': '1px solid #ddd', 'borderRadius': '4px'}
                        ),
                        dcc.Input(
                            id='keyword-2-input',
                            type='text',
                            placeholder='Keyword 2 (e.g., database)',
                            style={'width': '48%', 'padding': '6px', 'marginLeft': '2%', 'border': '1px solid #ddd', 'borderRadius': '4px'}
                        )
                    ], style={'marginBottom': 8}),
                    html.Div([
                        dcc.Input(
                            id='keyword-3-input',
                            type='text',
                            placeholder='Keyword 3 (e.g., AI)',
                            style={'width': '48%', 'padding': '6px', 'marginRight': '2%', 'border': '1px solid #ddd', 'borderRadius': '4px'}
                        ),
                        dcc.Input(
                            id='keyword-4-input',
                            type='text',
                            placeholder='Keyword 4 (e.g., neural networks)',
                            style={'width': '48%', 'padding': '6px', 'marginLeft': '2%', 'border': '1px solid #ddd', 'borderRadius': '4px'}
                        )
                    ], style={'marginBottom': 8}),
                    html.Div([
                        dcc.Input(
                            id='keyword-5-input',
                            type='text',
                            placeholder='Keyword 5 (e.g., big data)',
                            style={'width': '48%', 'padding': '6px', 'marginRight': '2%', 'border': '1px solid #ddd', 'borderRadius': '4px'}
                        ),
                        html.Button(
                            'Compare Keywords',
                            id='compare-keywords-button',
                            n_clicks=0,
                            style={'width': '48%', 'backgroundColor': '#e74c3c', 'color': 'white', 'padding': '8px 16px', 'marginLeft': '2%', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
                        )
                    ], style={'marginBottom': 15})
                ], style={'marginBottom': 15}),
                dcc.Graph(id='widget-2-graph'),
                html.Div(id='widget-2-info', style={'textAlign': 'center', 'marginTop': 10})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': 10})
        ]),
        
        # Row 2
        html.Div([
            # Widget 3 - University Keyword Analysis
            html.Div([
                html.H4("Widget 3 - University Keyword Analysis", style={'textAlign': 'center'}),
                html.Div([
                    html.Label("Select University:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                    dcc.Dropdown(
                        id='university-dropdown',
                        placeholder='Select a university...',
                        style={'marginBottom': 15}
                    ),
                    html.Button(
                        'Analyze Keywords',
                        id='analyze-keywords-button',
                        n_clicks=0,
                        style={'backgroundColor': '#9b59b6', 'color': 'white', 'padding': '8px 16px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
                    )
                ], style={'marginBottom': 15}),
                dcc.Graph(id='widget-3-graph'),
                html.Div(id='widget-3-info', style={'textAlign': 'center', 'marginTop': 10})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': 10}),
            
            # Widget 4 - Person Search
            html.Div([
                html.H4("Widget 4 - Person Search", style={'textAlign': 'center'}),
                html.Div([
                    html.Label("Enter Person Name:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                    dcc.Input(
                        id='person-name-input',
                        type='text',
                        placeholder='Enter a person\'s name...',
                        style={'width': '100%', 'padding': '8px', 'marginBottom': 10, 'border': '1px solid #ddd', 'borderRadius': '4px'}
                    ),
                    html.Button(
                        'Search',
                        id='search-button',
                        n_clicks=0,
                        style={'backgroundColor': '#27ae60', 'color': 'white', 'padding': '8px 16px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
                    )
                ], style={'marginBottom': 15}),
                html.Div(id='person-search-results', style={'textAlign': 'left', 'marginTop': 10})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': 10})
        ]),
        
        # Row 3
        html.Div([
            # Widget 5 - Time Series
            html.Div([
                html.H4("Widget 5 - Publications Over Time", style={'textAlign': 'center'}),
                dcc.Graph(id='widget-5-graph'),
                html.Div(id='widget-5-info', style={'textAlign': 'center', 'marginTop': 10})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': 10}),
            
            # Widget 6 - Faculty Publication Search
            html.Div([
                html.H4("Widget 6 - Faculty Publication Search", style={'textAlign': 'center'}),
                html.Div([
                    html.Label("Enter Faculty Member Name:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                    dcc.Input(
                        id='faculty-name-input',
                        type='text',
                        placeholder='Enter faculty member name...',
                        style={'width': '100%', 'padding': '8px', 'marginBottom': 10, 'border': '1px solid #ddd', 'borderRadius': '4px'}
                    ),
                    html.Button(
                        'Search Publications',
                        id='faculty-search-button',
                        n_clicks=0,
                        style={'backgroundColor': '#f39c12', 'color': 'white', 'padding': '8px 16px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
                    )
                ], style={'marginBottom': 15}),
                dcc.Graph(id='widget-6-graph'),
                html.Div(id='widget-6-info', style={'textAlign': 'center', 'marginTop': 10})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': 10})
        ])
    ]),
    
    # Refresh Button
    html.Div([
        html.Button('Refresh Dashboard', id='refresh-button', n_clicks=0,
                   style={'backgroundColor': '#3498db', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'borderRadius': 5})
    ], style={'textAlign': 'center', 'marginTop': 20}),
    
    # Hidden div for storing data
    html.Div(id='data-store', style={'display': 'none'})
], style={'padding': 20, 'fontFamily': 'Arial, sans-serif'})

# Callback to refresh all widgets
@app.callback(
    [Output('widget-1-graph', 'figure'),
     Output('widget-2-graph', 'figure'),
     Output('widget-3-graph', 'figure'),
     Output('widget-5-graph', 'figure'),
     Output('widget-6-graph', 'figure'),
     Output('widget-1-info', 'children'),
     Output('widget-2-info', 'children'),
     Output('widget-3-info', 'children'),
     Output('widget-5-info', 'children'),
     Output('widget-6-info', 'children')],
    [Input('refresh-button', 'n_clicks')]
)
def update_widgets(n_clicks):
    """Update all widgets with fresh data from databases"""
    
    # Widget 5 - Time Series
    widget5_fig, widget5_info = get_timeseries_widget_data()
    
    # Widget 6 - Summary Stats
    widget6_fig, widget6_info = get_summary_widget_data()
    
    # Create placeholder for Widget 1 (now handled by separate callback)
    widget1_fig = go.Figure().add_annotation(
        text="Use the keyword search above to find publications", 
        x=0.5, y=0.5, showarrow=False
    )
    widget1_info = "Widget 1 now uses keyword search"
    
    # Create placeholder for Widget 2 (now handled by separate callback)
    widget2_fig = go.Figure().add_annotation(
        text="Use the keyword comparison above to compare keywords", 
        x=0.5, y=0.5, showarrow=False
    )
    widget2_info = "Widget 2 now uses keyword comparison"
    
    # Create placeholder for Widget 3 (now handled by separate callback)
    widget3_fig = go.Figure().add_annotation(
        text="Use the university dropdown above to analyze keywords", 
        x=0.5, y=0.5, showarrow=False
    )
    widget3_info = "Widget 3 now uses university keyword analysis"
    
    return (widget1_fig, widget2_fig, widget3_fig, widget5_fig, widget6_fig,
            widget1_info, widget2_info, widget3_info, widget5_info, widget6_info)

# Callback for person search
@app.callback(
    Output('person-search-results', 'children'),
    [Input('search-button', 'n_clicks')],
    [dash.dependencies.State('person-name-input', 'value')]
)
def search_person(n_clicks, person_name):
    """Search for a person across all databases"""
    if not n_clicks or not person_name:
        return html.Div("Enter a person's name and click Search to find information.", 
                       style={'color': '#7f8c8d', 'fontStyle': 'italic'})
    
    try:
        results = get_person_information(person_name)
        return results
    except Exception as e:
        return html.Div(f"Error searching for person: {str(e)}", 
                       style={'color': 'red', 'fontWeight': 'bold'})

# Callback for keyword search
@app.callback(
    [Output('widget-1-graph', 'figure'),
     Output('widget-1-info', 'children')],
    [Input('keyword-search-button', 'n_clicks'),
     Input('show-all-button', 'n_clicks')],
    [dash.dependencies.State('keyword-input', 'value')]
)
def search_publications_by_keyword(search_clicks, show_all_clicks, keyword):
    """Search for publications by keyword or show all publications"""
    
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        # Initial load - show placeholder
        fig = go.Figure().add_annotation(
            text="Enter a keyword and click 'Search Publications' to find relevant publications", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, "Enter a keyword to search publications"
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        if button_id == 'keyword-search-button' and keyword:
            # Search by keyword
            fig, info = get_publications_by_keyword(keyword)
        elif button_id == 'show-all-button':
            # Show all publications
            fig, info = get_all_publications()
        else:
            # No keyword provided
            fig = go.Figure().add_annotation(
                text="Please enter a keyword to search", 
                x=0.5, y=0.5, showarrow=False
            )
            info = "No keyword provided"
        
        return fig, info
    except Exception as e:
        fig = go.Figure().add_annotation(
            text=f"Error: {str(e)}", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, f"Error searching publications: {str(e)}"

# Callback for keyword comparison
@app.callback(
    [Output('widget-2-graph', 'figure'),
     Output('widget-2-info', 'children')],
    [Input('compare-keywords-button', 'n_clicks')],
    [dash.dependencies.State('keyword-1-input', 'value'),
     dash.dependencies.State('keyword-2-input', 'value'),
     dash.dependencies.State('keyword-3-input', 'value'),
     dash.dependencies.State('keyword-4-input', 'value'),
     dash.dependencies.State('keyword-5-input', 'value')]
)
def compare_keywords(n_clicks, keyword1, keyword2, keyword3, keyword4, keyword5):
    """Compare 5 keywords and show their statistics"""
    
    if not n_clicks:
        # Initial load - show placeholder
        fig = go.Figure().add_annotation(
            text="Enter 5 keywords and click 'Compare Keywords' to see comparison", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, "Enter 5 keywords to compare their publication statistics"
    
    # Collect all non-empty keywords
    keywords = [kw.strip() for kw in [keyword1, keyword2, keyword3, keyword4, keyword5] if kw and kw.strip()]
    
    if len(keywords) < 2:
        fig = go.Figure().add_annotation(
            text="Please enter at least 2 keywords to compare", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, "Please enter at least 2 keywords to compare"
    
    try:
        fig, info = get_keyword_comparison(keywords)
        return fig, info
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        return fig, f"Error comparing keywords: {str(e)}"

# Callback to populate university dropdown
@app.callback(
    Output('university-dropdown', 'options'),
    [Input('refresh-button', 'n_clicks')]
)
def populate_university_dropdown(n_clicks):
    """Populate the university dropdown with available universities"""
    try:
        universities = get_available_universities()
        return universities
    except Exception as e:
        logger.error(f"Error populating university dropdown: {e}")
        return []

# Callback for university keyword analysis
@app.callback(
    [Output('widget-3-graph', 'figure'),
     Output('widget-3-info', 'children')],
    [Input('analyze-keywords-button', 'n_clicks')],
    [dash.dependencies.State('university-dropdown', 'value')]
)
def analyze_university_keywords(n_clicks, selected_university):
    """Analyze top keywords for selected university"""
    
    if not n_clicks or not selected_university:
        # Initial load - show placeholder
        fig = go.Figure().add_annotation(
            text="Select a university and click 'Analyze Keywords' to see top keywords", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, "Select a university to analyze its top research keywords"
    
    try:
        fig, info = get_university_keywords(selected_university)
        return fig, info
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        return fig, f"Error analyzing university keywords: {str(e)}"

# Callback for faculty publication search
@app.callback(
    [Output('widget-6-graph', 'figure'),
     Output('widget-6-info', 'children')],
    [Input('faculty-search-button', 'n_clicks')],
    [dash.dependencies.State('faculty-name-input', 'value')]
)
def search_faculty_publications(n_clicks, faculty_name):
    """Search for publications by a specific faculty member"""
    
    if not n_clicks or not faculty_name:
        # Initial load - show placeholder
        fig = go.Figure().add_annotation(
            text="Enter a faculty member name and click 'Search Publications' to find their publications", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, "Enter a faculty member name to search their publications"
    
    try:
        fig, info = get_faculty_publications(faculty_name)
        return fig, info
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        return fig, f"Error searching faculty publications: {str(e)}"

# Widget data functions - TO BE IMPLEMENTED BASED ON YOUR QUERIES
def get_publications_by_keyword(keyword):
    """Get publications by keyword from MySQL"""
    try:
        if mysql_conn and mysql_conn.connection:
            # Comprehensive search query that looks in title, abstract, and keywords
            query = """
            SELECT 
                p.title,
                p.year,
                p.venue,
                p.citations,
                p.abstract,
                GROUP_CONCAT(DISTINCT f.name SEPARATOR ', ') as authors
            FROM publication p
            LEFT JOIN publication_author pa ON p.id = pa.publication_id
            LEFT JOIN faculty f ON pa.faculty_id = f.id
            WHERE 
                p.title LIKE %s 
                OR p.abstract LIKE %s 
                OR p.keywords LIKE %s
                OR p.venue LIKE %s
            GROUP BY p.id, p.title, p.year, p.venue, p.citations, p.abstract
            ORDER BY p.citations DESC, p.year DESC
            LIMIT 20
            """
            
            search_term = f'%{keyword}%'
            results = mysql_conn.execute_query(query, (search_term, search_term, search_term, search_term))
            
            if results:
                # Create a bar chart showing publications by year
                df = pd.DataFrame(results, columns=['title', 'year', 'venue', 'citations', 'abstract', 'authors'])
                
                # Group by year and count publications
                year_counts = df.groupby('year').size().reset_index(name='count')
                year_counts = year_counts.sort_values('year')
                
                # Create bar chart
                fig = px.bar(
                    year_counts, 
                    x='year', 
                    y='count',
                    title=f"Publications containing '{keyword}' by Year",
                    labels={'year': 'Year', 'count': 'Number of Publications'},
                    color='count',
                    color_continuous_scale='viridis'
                )
                
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Number of Publications",
                    template='plotly_white',
                    height=400,
                    showlegend=False
                )
                
                # Add hover information
                fig.update_traces(
                    hovertemplate="<b>Year:</b> %{x}<br><b>Publications:</b> %{y}<extra></extra>"
                )
                
                # Calculate statistics
                total_pubs = len(df)
                avg_citations = df['citations'].mean() if 'citations' in df.columns else 0
                top_venue = df['venue'].mode().iloc[0] if len(df) > 0 else 'N/A'
                
                info = f"Found {total_pubs} publications | Avg Citations: {avg_citations:.1f} | Top Venue: {top_venue}"
                
            else:
                fig = go.Figure().add_annotation(
                    text=f"No publications found containing '{keyword}'", 
                    x=0.5, y=0.5, showarrow=False
                )
                info = f"No publications found for keyword: {keyword}"
        else:
            fig = go.Figure().add_annotation(
                text="MySQL not connected", 
                x=0.5, y=0.5, showarrow=False
            )
            info = "MySQL connection not available"
    except Exception as e:
        fig = go.Figure().add_annotation(
            text=f"Error: {str(e)}", 
            x=0.5, y=0.5, showarrow=False
        )
        info = f"Error searching publications: {str(e)}"
    
    return fig, info

def get_all_publications():
    """Get all publications from MySQL"""
    try:
        if mysql_conn and mysql_conn.connection:
            # Query to get all publications with basic info
            query = """
            SELECT 
                p.title,
                p.year,
                p.venue,
                p.citations,
                GROUP_CONCAT(DISTINCT f.name SEPARATOR ', ') as authors
            FROM publication p
            LEFT JOIN publication_author pa ON p.id = pa.publication_id
            LEFT JOIN faculty f ON pa.faculty_id = f.id
            GROUP BY p.id, p.title, p.year, p.venue, p.citations
            ORDER BY p.citations DESC, p.year DESC
            LIMIT 50
            """
            
            results = mysql_conn.execute_query(query)
            
            if results:
                df = pd.DataFrame(results, columns=['title', 'year', 'venue', 'citations', 'authors'])
                
                # Create a scatter plot of citations vs year
                fig = px.scatter(
                    df, 
                    x='year', 
                    y='citations',
                    title="All Publications: Citations vs Year",
                    labels={'year': 'Year', 'citations': 'Citations'},
                    hover_data=['title', 'venue', 'authors'],
                    size='citations',
                    color='citations',
                    color_continuous_scale='viridis'
                )
                
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Citations",
                    template='plotly_white',
                    height=400
                )
                
                # Calculate statistics
                total_pubs = len(df)
                avg_citations = df['citations'].mean() if 'citations' in df.columns else 0
                max_citations = df['citations'].max() if 'citations' in df.columns else 0
                
                info = f"Showing {total_pubs} publications | Avg Citations: {avg_citations:.1f} | Max Citations: {max_citations}"
                
            else:
                fig = go.Figure().add_annotation(
                    text="No publications found in database", 
                    x=0.5, y=0.5, showarrow=False
                )
                info = "No publications found in database"
        else:
            fig = go.Figure().add_annotation(
                text="MySQL not connected", 
                x=0.5, y=0.5, showarrow=False
            )
            info = "MySQL connection not available"
    except Exception as e:
        fig = go.Figure().add_annotation(
            text=f"Error: {str(e)}", 
            x=0.5, y=0.5, showarrow=False
        )
        info = f"Error retrieving publications: {str(e)}"
    
    return fig, info

def get_keyword_comparison(keywords):
    """Compare multiple keywords and show their publication statistics"""
    try:
        if not mysql_conn or not mysql_conn.connection:
            fig = go.Figure().add_annotation(
                text="MySQL not connected", 
                x=0.5, y=0.5, showarrow=False
            )
            return fig, "MySQL connection not available"
        
        # Collect data for each keyword
        keyword_data = []
        
        for keyword in keywords:
            # Search for publications containing this keyword
            query = """
            SELECT 
                COUNT(*) as publication_count,
                AVG(citations) as avg_citations,
                MAX(citations) as max_citations,
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                COUNT(DISTINCT venue) as unique_venues
            FROM publications 
            WHERE LOWER(title) LIKE LOWER(%s) 
               OR LOWER(abstract) LIKE LOWER(%s) 
               OR LOWER(keywords) LIKE LOWER(%s)
               OR LOWER(venue) LIKE LOWER(%s)
            """
            
            search_term = f"%{keyword}%"
            results = mysql_conn.execute_query(query, (search_term, search_term, search_term, search_term))
            
            if results and len(results) > 0:
                row = results[0]
                keyword_data.append({
                    'keyword': keyword,
                    'publication_count': row[0] or 0,
                    'avg_citations': float(row[1]) if row[1] else 0,
                    'max_citations': row[2] or 0,
                    'earliest_year': row[3] or 0,
                    'latest_year': row[4] or 0,
                    'unique_venues': row[5] or 0
                })
            else:
                keyword_data.append({
                    'keyword': keyword,
                    'publication_count': 0,
                    'avg_citations': 0,
                    'max_citations': 0,
                    'earliest_year': 0,
                    'latest_year': 0,
                    'unique_venues': 0
                })
        
        if not keyword_data:
            fig = go.Figure().add_annotation(
                text="No data found for any keywords", 
                x=0.5, y=0.5, showarrow=False
            )
            return fig, "No data found for any keywords"
        
        # Create comparison visualizations
        df = pd.DataFrame(keyword_data)
        
        # Create subplots for different metrics
        fig = go.Figure()
        
        # Add bar chart for publication count
        fig.add_trace(go.Bar(
            x=df['keyword'],
            y=df['publication_count'],
            name='Publication Count',
            marker_color='#3498db',
            text=df['publication_count'],
            textposition='auto'
        ))
        
        # Add line chart for average citations (secondary y-axis)
        fig.add_trace(go.Scatter(
            x=df['keyword'],
            y=df['avg_citations'],
            name='Avg Citations',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8)
        ))
        
        # Update layout
        fig.update_layout(
            title="Keyword Comparison: Publication Count vs Average Citations",
            xaxis_title="Keywords",
            yaxis=dict(title="Publication Count", side="left"),
            yaxis2=dict(title="Average Citations", side="right", overlaying="y"),
            template='plotly_white',
            height=500,
            showlegend=True,
            legend=dict(x=0.02, y=0.98)
        )
        
        # Create summary statistics
        total_pubs = df['publication_count'].sum()
        avg_citations_overall = df['avg_citations'].mean()
        most_popular = df.loc[df['publication_count'].idxmax(), 'keyword'] if len(df) > 0 else "None"
        highest_cited = df.loc[df['avg_citations'].idxmax(), 'keyword'] if len(df) > 0 else "None"
        
        info = f"Total Publications: {total_pubs} | Avg Citations: {avg_citations_overall:.1f} | Most Popular: {most_popular} | Highest Cited: {highest_cited}"
        
        return fig, info
        
    except Exception as e:
        fig = go.Figure().add_annotation(
            text=f"Error: {str(e)}", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, f"Error comparing keywords: {str(e)}"

def get_available_universities():
    """Get list of available universities from the database"""
    try:
        if mysql_conn and mysql_conn.connection:
            # Query to get distinct universities
            query = """
            SELECT DISTINCT university 
            FROM faculty 
            WHERE university IS NOT NULL AND university != ''
            ORDER BY university
            """
            results = mysql_conn.execute_query(query)
            
            if results:
                # Format for dropdown options
                options = [{'label': row[0], 'value': row[0]} for row in results]
                return options
            else:
                return []
        else:
            logger.warning("MySQL not connected for university list")
            return []
    except Exception as e:
        logger.error(f"Error getting universities: {e}")
        return []

def get_university_keywords(university_name):
    """Get top 10 keywords for a specific university"""
    try:
        if not mysql_conn or not mysql_conn.connection:
            fig = go.Figure().add_annotation(
                text="MySQL not connected", 
                x=0.5, y=0.5, showarrow=False
            )
            return fig, "MySQL connection not available"
        
        # Query to get keywords from publications by faculty at the selected university
        query = """
        SELECT 
            p.keywords,
            COUNT(*) as keyword_count
        FROM publication p
        JOIN publication_author pa ON p.id = pa.publication_id
        JOIN faculty f ON pa.faculty_id = f.id
        WHERE f.university = %s 
            AND p.keywords IS NOT NULL 
            AND p.keywords != ''
        GROUP BY p.keywords
        ORDER BY keyword_count DESC
        LIMIT 10
        """
        
        results = mysql_conn.execute_query(query, (university_name,))
        
        if results:
            # Process keywords - split comma-separated keywords and count individual ones
            keyword_counts = {}
            
            for row in results:
                keywords = row[0].split(',') if row[0] else []
                count = row[1]
                
                for keyword in keywords:
                    keyword = keyword.strip().lower()
                    if keyword and len(keyword) > 2:  # Filter out very short keywords
                        if keyword in keyword_counts:
                            keyword_counts[keyword] += count
                        else:
                            keyword_counts[keyword] = count
            
            # Sort by count and get top 10
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if sorted_keywords:
                # Create pie chart
                keywords, counts = zip(*sorted_keywords)
                
                fig = go.Figure(data=[go.Pie(
                    labels=keywords,
                    values=counts,
                    hole=0.3,  # Create a donut chart
                    marker_colors=px.colors.qualitative.Set3,
                    textinfo='label+percent',
                    textposition='inside',
                    insidetextorientation='radial'
                )])
                
                fig.update_layout(
                    title=f"Top 10 Research Keywords at {university_name}",
                    template='plotly_white',
                    height=500,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=1.02
                    )
                )
                
                # Calculate statistics
                total_keywords = sum(counts)
                most_common = keywords[0] if keywords else "None"
                unique_keywords = len(keyword_counts)
                
                info = f"Total Keyword Mentions: {total_keywords} | Most Common: {most_common} | Unique Keywords: {unique_keywords}"
                
                return fig, info
            else:
                fig = go.Figure().add_annotation(
                    text=f"No keywords found for {university_name}", 
                    x=0.5, y=0.5, showarrow=False
                )
                return fig, f"No keywords found for {university_name}"
        else:
            fig = go.Figure().add_annotation(
                text=f"No data found for {university_name}", 
                x=0.5, y=0.5, showarrow=False
            )
            return fig, f"No data found for {university_name}"
            
    except Exception as e:
        fig = go.Figure().add_annotation(
            text=f"Error: {str(e)}", 
            x=0.5, y=0.5, showarrow=False
        )
        return fig, f"Error analyzing university keywords: {str(e)}"

def get_mongodb_widget_data():
    """Get data for Widget 2 from MongoDB"""
    try:
        if mongodb_conn and mongodb_conn.client:
            # TODO: Replace with your MongoDB query
            collection_name = "your_collection"  # CHANGE: Your collection name
            documents = mongodb_conn.find_documents(collection_name, limit=10)
            
            if documents:
                # Create sample data - replace with your actual data processing
                df = pd.DataFrame(documents)
                fig = px.scatter(df, x=df.columns[0] if len(df.columns) > 0 else 'index', 
                               y=df.columns[1] if len(df.columns) > 1 else 'index', 
                               title="MongoDB Data")
                info = f"Data from MongoDB: {len(documents)} documents"
            else:
                fig = go.Figure().add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
                info = "No data available from MongoDB"
        else:
            fig = go.Figure().add_annotation(text="MongoDB not connected", x=0.5, y=0.5, showarrow=False)
            info = "MongoDB connection not available"
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        info = f"Error accessing MongoDB: {str(e)}"
    
    return fig, info

def get_neo4j_widget_data():
    """Get data for Widget 3 from Neo4j"""
    try:
        if neo4j_conn and neo4j_conn.driver:
            # TODO: Replace with your Neo4j query
            query = "MATCH (n) RETURN count(n) as node_count"  # Placeholder query
            results = neo4j_conn.execute_query(query)
            
            if results:
                # Create sample data - replace with your actual data processing
                df = pd.DataFrame(results)
                fig = px.pie(df, values=df.columns[0] if len(df.columns) > 0 else 'index', 
                           names=df.columns[0] if len(df.columns) > 0 else 'index', 
                           title="Neo4j Data")
                info = f"Data from Neo4j: {len(results)} results"
            else:
                fig = go.Figure().add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
                info = "No data available from Neo4j"
        else:
            fig = go.Figure().add_annotation(text="Neo4j not connected", x=0.5, y=0.5, showarrow=False)
            info = "Neo4j connection not available"
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        info = f"Error accessing Neo4j: {str(e)}"
    
    return fig, info

def get_person_information(person_name):
    """Get comprehensive information about a person from all databases"""
    all_results = []
    
    # MySQL Search
    if mysql_conn and mysql_conn.connection:
        try:
            # Search in faculty table
            faculty_query = """
            SELECT id, name, email, phone, position, research, interests, department, university
            FROM faculty 
            WHERE name LIKE %s
            """
            faculty_results = mysql_conn.execute_query(faculty_query, (f'%{person_name}%',))
            
            if faculty_results:
                all_results.append(html.H5("📊 MySQL - Faculty Information", style={'color': '#2980b9', 'marginTop': 20}))
                for faculty in faculty_results:
                    faculty_info = html.Div([
                        html.Strong(f"Name: {faculty[1]}"),
                        html.Br(),
                        html.Span(f"Email: {faculty[2] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Position: {faculty[4] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Department: {faculty[7] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"University: {faculty[8] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Research: {faculty[5] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Interests: {faculty[6] or 'N/A'}")
                    ], style={'backgroundColor': '#f8f9fa', 'padding': 10, 'margin': 5, 'borderRadius': 5, 'border': '1px solid #dee2e6'})
                    all_results.append(faculty_info)
            
            # Search in publications table for author
            pub_query = """
            SELECT p.title, p.year, p.venue, p.citations
            FROM publication p
            JOIN publication_author pa ON p.id = pa.publication_id
            JOIN faculty f ON pa.faculty_id = f.id
            WHERE f.name LIKE %s
            ORDER BY p.year DESC
            LIMIT 10
            """
            pub_results = mysql_conn.execute_query(pub_query, (f'%{person_name}%',))
            
            if pub_results:
                all_results.append(html.H5("📚 MySQL - Publications", style={'color': '#2980b9', 'marginTop': 20}))
                for pub in pub_results:
                    pub_info = html.Div([
                        html.Strong(f"Title: {pub[0]}"),
                        html.Br(),
                        html.Span(f"Year: {pub[1] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Venue: {pub[2] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Citations: {pub[3] or 0}")
                    ], style={'backgroundColor': '#e8f5e8', 'padding': 10, 'margin': 5, 'borderRadius': 5, 'border': '1px solid #c3e6c3'})
                    all_results.append(pub_info)
                    
        except Exception as e:
            logger.warning(f"MySQL person search failed: {e}")
    
    # MongoDB Search
    if mongodb_conn and mongodb_conn.client:
        try:
            # Search in faculty collection
            faculty_filter = {"name": {"$regex": person_name, "$options": "i"}}
            faculty_docs = mongodb_conn.find_documents("faculty", faculty_filter, limit=5)
            
            if faculty_docs:
                all_results.append(html.H5("🍃 MongoDB - Faculty Information", style={'color': '#27ae60', 'marginTop': 20}))
                for faculty in faculty_docs:
                    faculty_info = html.Div([
                        html.Strong(f"Name: {faculty.get('name', 'N/A')}"),
                        html.Br(),
                        html.Span(f"Email: {faculty.get('email', 'N/A')}"),
                        html.Br(),
                        html.Span(f"Position: {faculty.get('position', 'N/A')}"),
                        html.Br(),
                        html.Span(f"Department: {faculty.get('department', 'N/A')}"),
                        html.Br(),
                        html.Span(f"Research Areas: {', '.join(faculty.get('research_areas', [])) if faculty.get('research_areas') else 'N/A'}")
                    ], style={'backgroundColor': '#f0f8f0', 'padding': 10, 'margin': 5, 'borderRadius': 5, 'border': '1px solid #a8e6a8'})
                    all_results.append(faculty_info)
            
            # Search in publications collection
            pub_filter = {"authors": {"$regex": person_name, "$options": "i"}}
            pub_docs = mongodb_conn.find_documents("publications", pub_filter, limit=5)
            
            if pub_docs:
                all_results.append(html.H5("🍃 MongoDB - Publications", style={'color': '#27ae60', 'marginTop': 20}))
                for pub in pub_docs:
                    pub_info = html.Div([
                        html.Strong(f"Title: {pub.get('title', 'N/A')}"),
                        html.Br(),
                        html.Span(f"Year: {pub.get('year', 'N/A')}"),
                        html.Br(),
                        html.Span(f"Authors: {', '.join(pub.get('authors', [])) if pub.get('authors') else 'N/A'}"),
                        html.Br(),
                        html.Span(f"Citations: {pub.get('citations', 0)}")
                    ], style={'backgroundColor': '#e8f5e8', 'padding': 10, 'margin': 5, 'borderRadius': 5, 'border': '1px solid #c3e6c3'})
                    all_results.append(pub_info)
                    
        except Exception as e:
            logger.warning(f"MongoDB person search failed: {e}")
    
    # Neo4j Search
    if neo4j_conn and neo4j_conn.driver:
        try:
            # Search for Person nodes
            person_query = """
            MATCH (p:Person)
            WHERE p.name CONTAINS $name
            RETURN p.name as name, p.email as email, p.position as position, p.department as department
            LIMIT 5
            """
            person_results = neo4j_conn.execute_query(person_query, {"name": person_name})
            
            if person_results:
                all_results.append(html.H5("🕸️ Neo4j - Person Information", style={'color': '#e67e22', 'marginTop': 20}))
                for person in person_results:
                    person_info = html.Div([
                        html.Strong(f"Name: {person[0] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Email: {person[1] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Position: {person[2] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Department: {person[3] or 'N/A'}")
                    ], style={'backgroundColor': '#fff8e1', 'padding': 10, 'margin': 5, 'borderRadius': 5, 'border': '1px solid #ffcc80'})
                    all_results.append(person_info)
            
            # Search for publications by this person
            pub_query = """
            MATCH (p:Person)-[:AUTHORED]->(pub:Publication)
            WHERE p.name CONTAINS $name
            RETURN pub.title as title, pub.year as year, pub.venue as venue, pub.citations as citations
            ORDER BY pub.year DESC
            LIMIT 10
            """
            pub_results = neo4j_conn.execute_query(pub_query, {"name": person_name})
            
            if pub_results:
                all_results.append(html.H5("🕸️ Neo4j - Publications", style={'color': '#e67e22', 'marginTop': 20}))
                for pub in pub_results:
                    pub_info = html.Div([
                        html.Strong(f"Title: {pub[0] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Year: {pub[1] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Venue: {pub[2] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Citations: {pub[3] or 0}")
                    ], style={'backgroundColor': '#e8f5e8', 'padding': 10, 'margin': 5, 'borderRadius': 5, 'border': '1px solid #c3e6c3'})
                    all_results.append(pub_info)
            
            # Search for collaborations
            collab_query = """
            MATCH (p1:Person)-[:AUTHORED]->(pub:Publication)<-[:AUTHORED]-(p2:Person)
            WHERE p1.name CONTAINS $name AND p1 <> p2
            RETURN p2.name as collaborator, count(pub) as collaboration_count
            ORDER BY collaboration_count DESC
            LIMIT 5
            """
            collab_results = neo4j_conn.execute_query(collab_query, {"name": person_name})
            
            if collab_results:
                all_results.append(html.H5("🕸️ Neo4j - Top Collaborators", style={'color': '#e67e22', 'marginTop': 20}))
                for collab in collab_results:
                    collab_info = html.Div([
                        html.Strong(f"Collaborator: {collab[0] or 'N/A'}"),
                        html.Br(),
                        html.Span(f"Joint Publications: {collab[1] or 0}")
                    ], style={'backgroundColor': '#f3e5f5', 'padding': 10, 'margin': 5, 'borderRadius': 5, 'border': '1px solid #ce93d8'})
                    all_results.append(collab_info)
                    
        except Exception as e:
            logger.warning(f"Neo4j person search failed: {e}")
    
    # If no results found
    if not all_results:
        return html.Div([
            html.H5("🔍 Search Results", style={'color': '#e74c3c'}),
            html.P(f"No information found for '{person_name}' in any database.", 
                   style={'color': '#7f8c8d', 'fontStyle': 'italic'})
        ])
    
    # Return all results
    return html.Div([
        html.H4(f"🔍 Search Results for '{person_name}'", style={'color': '#2c3e50', 'marginBottom': 20}),
        html.Div(all_results)
    ])

def get_timeseries_widget_data():
    """Get data for Widget 5 - Publications Over Time"""
    try:
        # Try to get publication data from different databases
        publication_data = []
        
        # Try MySQL first (assuming publications table)
        if mysql_conn and mysql_conn.connection:
            try:
                query = """
                SELECT DATE(publication_date) as date, COUNT(*) as count 
                FROM publications 
                WHERE publication_date IS NOT NULL 
                GROUP BY DATE(publication_date) 
                ORDER BY date
                """
                results = mysql_conn.execute_query(query)
                if results:
                    for row in results:
                        publication_data.append({
                            'date': row[0],
                            'count': row[1],
                            'source': 'MySQL'
                        })
            except Exception as e:
                logger.warning(f"MySQL publications query failed: {e}")
        
        # Try MongoDB (assuming publications collection)
        if mongodb_conn and mongodb_conn.client and not publication_data:
            try:
                pipeline = [
                    {"$match": {"publication_date": {"$exists": True}}},
                    {"$group": {
                        "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$publication_date"}},
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"_id": 1}}
                ]
                collection_name = "publications"
                documents = mongodb_conn.execute_aggregation(collection_name, pipeline)
                if documents:
                    for doc in documents:
                        publication_data.append({
                            'date': doc['_id'],
                            'count': doc['count'],
                            'source': 'MongoDB'
                        })
            except Exception as e:
                logger.warning(f"MongoDB publications query failed: {e}")
        
        # Try Neo4j (assuming Publication nodes)
        if neo4j_conn and neo4j_conn.driver and not publication_data:
            try:
                query = """
                MATCH (p:Publication)
                WHERE p.publication_date IS NOT NULL
                RETURN date(p.publication_date) as date, count(p) as count
                ORDER BY date
                """
                results = neo4j_conn.execute_query(query)
                if results:
                    for row in results:
                        publication_data.append({
                            'date': row[0],
                            'count': row[1],
                            'source': 'Neo4j'
                        })
            except Exception as e:
                logger.warning(f"Neo4j publications query failed: {e}")
        
        # If no real data found, create sample data for demonstration
        if not publication_data:
            # Generate sample publication data for the last 12 months
            from datetime import datetime, timedelta
            import random
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            current_date = start_date
            
            while current_date <= end_date:
                # Simulate more publications on weekdays and fewer on weekends
                base_count = 5 if current_date.weekday() < 5 else 2
                count = base_count + random.randint(-2, 3)
                count = max(0, count)  # Ensure non-negative
                
                publication_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'count': count,
                    'source': 'Sample Data'
                })
                current_date += timedelta(days=1)
        
        # Create the time series visualization
        if publication_data:
            df = pd.DataFrame(publication_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Create line chart with area fill
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['count'],
                mode='lines+markers',
                name='Publications',
                line=dict(color='#1f77b4', width=3),
                fill='tonexty',
                fillcolor='rgba(31, 119, 180, 0.2)',
                marker=dict(size=6, color='#1f77b4')
            ))
            
            fig.update_layout(
                title="Publications Over Time",
                xaxis_title="Date",
                yaxis_title="Number of Publications",
                hovermode='x unified',
                template='plotly_white',
                height=400,
                showlegend=True
            )
            
            # Add range slider for better navigation
            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all", label="All")
                    ])
                )
            )
            
            total_pubs = df['count'].sum()
            avg_daily = df['count'].mean()
            source = df['source'].iloc[0]
            info = f"Total Publications: {total_pubs} | Avg Daily: {avg_daily:.1f} | Source: {source}"
        else:
            fig = go.Figure().add_annotation(
                text="No publication data available", 
                x=0.5, y=0.5, showarrow=False
            )
            info = "No publication data found in any database"
            
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        info = f"Error in publications widget: {str(e)}"
    
    return fig, info

def get_faculty_publications(faculty_name):
    """Get all publications by a specific faculty member"""
    try:
        if not mysql_conn or not mysql_conn.connection:
            fig = go.Figure().add_annotation(
                text="MySQL not connected", 
                x=0.5, y=0.5, showarrow=False
            )
            return fig, "MySQL connection not available"
        
        # Query to get publications by faculty member
        query = """
        SELECT 
            p.title,
            p.year,
            p.venue,
            p.citations,
            p.abstract,
            p.keywords,
            f.name as faculty_name,
            f.university,
            f.department
        FROM publication p
        JOIN publication_author pa ON p.id = pa.publication_id
        JOIN faculty f ON pa.faculty_id = f.id
        WHERE f.name LIKE %s
        ORDER BY p.year DESC, p.citations DESC
        """
        
        search_term = f'%{faculty_name}%'
        results = mysql_conn.execute_query(query, (search_term,))
        
        if results:
            # Create DataFrame
            df = pd.DataFrame(results, columns=['title', 'year', 'venue', 'citations', 'abstract', 'keywords', 'faculty_name', 'university', 'department'])
            
            # Create multiple visualizations
            fig = go.Figure()
            
            # Create subplots for different views
            from plotly.subplots import make_subplots
            
            # Create subplots: 1 row, 2 columns
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Publications by Year', 'Citations Distribution', 'Top Venues', 'Research Timeline'),
                specs=[[{"type": "bar"}, {"type": "histogram"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # 1. Publications by Year (Bar Chart)
            year_counts = df.groupby('year').size().reset_index(name='count')
            year_counts = year_counts.sort_values('year')
            
            fig.add_trace(
                go.Bar(x=year_counts['year'], y=year_counts['count'], name='Publications', marker_color='#3498db'),
                row=1, col=1
            )
            
            # 2. Citations Distribution (Histogram)
            fig.add_trace(
                go.Histogram(x=df['citations'], name='Citations', nbinsx=20, marker_color='#e74c3c'),
                row=1, col=2
            )
            
            # 3. Top Venues (Bar Chart)
            venue_counts = df.groupby('venue').size().reset_index(name='count')
            venue_counts = venue_counts.sort_values('count', ascending=False).head(10)
            
            fig.add_trace(
                go.Bar(x=venue_counts['venue'], y=venue_counts['count'], name='Venues', marker_color='#2ecc71'),
                row=2, col=1
            )
            
            # 4. Research Timeline (Scatter Plot)
            fig.add_trace(
                go.Scatter(
                    x=df['year'], 
                    y=df['citations'], 
                    mode='markers',
                    name='Publications',
                    marker=dict(
                        size=df['citations']/10 + 5,  # Size based on citations
                        color=df['citations'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Citations")
                    ),
                    text=df['title'],
                    hovertemplate="<b>%{text}</b><br>Year: %{x}<br>Citations: %{y}<extra></extra>"
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title=f"Publications by {faculty_name}",
                height=600,
                showlegend=False,
                template='plotly_white'
            )
            
            # Update axes labels
            fig.update_xaxes(title_text="Year", row=1, col=1)
            fig.update_yaxes(title_text="Number of Publications", row=1, col=1)
            fig.update_xaxes(title_text="Citations", row=1, col=2)
            fig.update_yaxes(title_text="Frequency", row=1, col=2)
            fig.update_xaxes(title_text="Venue", row=2, col=1)
            fig.update_yaxes(title_text="Number of Publications", row=2, col=1)
            fig.update_xaxes(title_text="Year", row=2, col=2)
            fig.update_yaxes(title_text="Citations", row=2, col=2)
            
            # Calculate statistics
            total_pubs = len(df)
            total_citations = df['citations'].sum()
            avg_citations = df['citations'].mean()
            h_index = len(df[df['citations'] >= df['citations'].rank(ascending=False)])
            years_active = df['year'].max() - df['year'].min() + 1
            top_venue = df['venue'].mode().iloc[0] if len(df) > 0 else 'N/A'
            university = df['university'].iloc[0] if len(df) > 0 else 'N/A'
            department = df['department'].iloc[0] if len(df) > 0 else 'N/A'
            
            info = f"Total Publications: {total_pubs} | Total Citations: {total_citations} | Avg Citations: {avg_citations:.1f} | H-index: {h_index} | Years Active: {years_active} | Top Venue: {top_venue} | University: {university} | Department: {department}"
            
        else:
            fig = go.Figure().add_annotation(
                text=f"No publications found for faculty member '{faculty_name}'", 
                x=0.5, y=0.5, showarrow=False
            )
            info = f"No publications found for faculty member: {faculty_name}"
            
    except Exception as e:
        fig = go.Figure().add_annotation(
            text=f"Error: {str(e)}", 
            x=0.5, y=0.5, showarrow=False
        )
        info = f"Error searching faculty publications: {str(e)}"
    
    return fig, info

def get_summary_widget_data():
    """Get data for Widget 6 - Summary Statistics (now Faculty Publication Search)"""
    try:
        # This function is now replaced by the faculty search functionality
        fig = go.Figure().add_annotation(
            text="Enter a faculty member name above to search their publications", 
            x=0.5, y=0.5, showarrow=False
        )
        info = "Widget 6 now allows faculty publication search"
    except Exception as e:
        fig = go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5, showarrow=False)
        info = f"Error in faculty search widget: {str(e)}"
    
    return fig, info

if __name__ == '__main__':
    print("Starting Multi-Database Dashboard...")
    print("=" * 50)
    print("DATABASE CONNECTION SETUP REQUIRED:")
    print("1. Modify the connection parameters in the initialize_database_connections() function")
    print("2. Set environment variables for automatic connection")
    print("3. Implement your specific queries in the widget data functions")
    print("=" * 50)
    
    app.run_server(debug=True, host='0.0.0.0', port=8050)
