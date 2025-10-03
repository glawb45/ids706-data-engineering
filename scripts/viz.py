import os
import psycopg2
from dotenv import load_dotenv

# Load .env if present (does nothing if file not found)
load_dotenv()

DB_NAME = os.getenv("DB_NAME", os.getenv("PGDATABASE", "duke_restaurants"))
DB_USER = os.getenv("DB_USER", os.getenv("PGUSER", "vscode"))
DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("PGPASSWORD", "vscode"))
# In devcontainer, host is 'db'; on your laptop use 'localhost'
DB_HOST = os.getenv("DB_HOST", os.getenv("PGHOST", "localhost"))
DB_PORT = os.getenv("DB_PORT", os.getenv("PGPORT", "5432"))


cur = conn.cursor()

# Define search parameters
min_rating = 4.0

# Execute search query
cur.execute("""
    SELECT name, address, rating, cuisine, avg_cost
    FROM restaurants
    WHERE rating >= %s
    ORDER BY rating DESC;
""", (min_rating,))

# Fetch and convert results to DataFrame

rows = cur.fetchall()
df = pd.DataFrame(rows, columns=['name', 'address', 'rating', 'cuisine', 'avg_cost'])

# Group by cuisine and calculate average cost
avg_cost_by_cuisine = df.groupby('cuisine')['avg_cost'].mean().reset_index()

# Create a bar chart of average cost by cuisine
fig = px.bar(avg_cost_by_cuisine, x='cuisine', y='avg_cost',
             title='Average Cost by Cuisine (Rating ≥ 4.0)',
             labels={'avg_cost': 'Average Cost', 'cuisine': 'Cuisine'})

# Save the plot as HTML file (just to make it interactive)
fig.write_html('avg_cost_by_cuisine.html')

# Close the connection
cur.close()
conn.close()