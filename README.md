# SQL Guidebook

This dataset is originally from a dataset I have used in RStudio. I have split the data into four separate files and tables: Games, Player_Stats, Players and Teams.

First, in our terminal we run the following to create the database:

```bash
sqlite3 nba.db
```

We may create the first table in our database, which we will call "Teams." We will build upon this table as the primary table in our database. We can run the below query to create this table:

```sql
CREATE TABLE IF NOT EXISTS Players (
  "player_id"   INTEGER PRIMARY KEY,
  "team_id" INTEGER,
  "league_id"       VARCHAR(100),
  "first_name"   VARCHAR(100),
  "last_name" VARCHAR(100),
  "full_name" VARCHAR(100),
  "jersey_number" INTEGER,
  "position_simple" VARCHAR(100),
  "status" VARCHAR(100),
  FOREIGN KEY ("team_id") REFERENCES Teams("team_id")
);
```