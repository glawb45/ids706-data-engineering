# import psycopg2
# from psycopg2 import sql
import sqlite3
import pandas as pd
import os

# --- Database connection setup ---
conn = sqlite3.connect("university_database.db")
cur = conn.cursor()

# --- Question 1: Insert data ---
print("Inserting Duke Tech record...")
cur.execute("""
    INSERT INTO university_rankings (institution, country, world_rank, score, year)
    VALUES ('Duke Tech', 'USA', 350, 60.5, 2014);
""")
conn.commit()

# --- Question 2: Count institutions from Japan ranked <= 200 in 2013 ---
print("\nCounting Japanese institutions ranked <= 200 in 2013...")
cur.execute("""
    SELECT country, COUNT(institution) AS count
    FROM university_rankings
    WHERE world_rank <= 200 
      AND year = 2013 
      AND country = 'Japan'
    GROUP BY country;
""")
for row in cur.fetchall():
    print(row)

# --- Question 3: Update University of Oxford’s score ---
print("\nUpdating University of Oxford score...")
cur.execute("""
    UPDATE university_rankings
    SET score = score + 1.2
    WHERE institution = 'University of Oxford' AND year = 2014;
""")
conn.commit()

# --- Question 4: Delete records from 2015 with score < 45 ---
print("\nDeleting low-score 2015 records...")
cur.execute("""
    DELETE FROM university_rankings
    WHERE year = 2015 AND score < 45;
""")
conn.commit()

# --- Show all remaining records ---
print("\nAll records in university_rankings:")
cur.execute("SELECT * FROM university_rankings;")
for row in cur.fetchall():
    print(row)

# --- Show Oxford 2014 data ---
print("\nUniversity of Oxford (2014):")
cur.execute("""
    SELECT institution, country, score, year
    FROM university_rankings
    WHERE institution = 'University of Oxford' AND year = 2014;
""")
for row in cur.fetchall():
    print(row)

# --- Show Duke Tech data ---
print("\nDuke Tech record:")
cur.execute("""
    SELECT institution, country, world_rank, score, year
    FROM university_rankings
    WHERE institution = 'Duke Tech';
""")
for row in cur.fetchall():
    print(row)

# --- Close connection ---
cur.close()
conn.close()
print("\nAll queries executed successfully.")