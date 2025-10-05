import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import webbrowser

# Load .env if present
load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("DB_NAME", os.getenv("PGDATABASE", "duke_restaurants"))
DB_USER = os.getenv("DB_USER", os.getenv("PGUSER", "vscode"))
DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("PGPASSWORD", "vscode"))
DB_HOST = os.getenv("DB_HOST", os.getenv("PGHOST", "localhost"))
DB_PORT = os.getenv("DB_PORT", os.getenv("PGPORT", "5432"))

# Connect to database
print("Connecting to database...")
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
print("Connected!")

cur = conn.cursor()

# Define search parameters
min_rating = 4.0

# Execute query
print(f"Fetching restaurants with rating >= {min_rating}...")
cur.execute("""
    SELECT name, address, rating, cuisine, avg_cost
    FROM restaurants
    WHERE rating >= %s
    ORDER BY rating DESC;
""", (min_rating,))

rows = cur.fetchall()
print(f"Fetched {len(rows)} rows")

# Convert to DataFrame
df = pd.DataFrame(rows, columns=['name', 'address', 'rating', 'cuisine', 'avg_cost'])
print("DataFrame created")

# Group by cuisine and calculate average cost
avg_cost_by_cuisine = df.groupby('cuisine')['avg_cost'].mean().reset_index()

# Create bar chart
fig = px.bar(avg_cost_by_cuisine, x='cuisine', y='avg_cost',
             title=f'Average Cost by Cuisine (Rating ≥ {min_rating})',
             labels={'avg_cost': 'Average Cost', 'cuisine': 'Cuisine'})

# Save plot as HTML
html_file = 'avg_cost_by_cuisine.html'
fig.write_html(html_file)
print(f"HTML plot saved: {html_file}")

# Open HTML plot in default web browser
webbrowser.open(html_file)
print("Plot opened in web browser!")

# Close database connection
cur.close()
conn.close()
print("Database connection closed")