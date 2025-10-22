# SQL Guidebook

This dataset is originally from a dataset I have used in RStudio. I have split the data into four separate files and tables: Games, Player_Stats, Players and Teams.

First, in our terminal we run the following to create the database:

```bash
sqlite3 nba.db
```

We may create the first table in our database, which we will call "Teams." We will build upon this table as the primary table in our database. We can run the below query to create this table:

```sql
CREATE TABLE IF NOT EXISTS Teams (
  "team_id" VARCHAR(100) PRIMARY KEY,
  "league_id"  VARCHAR(100),
  "team_full_name" VARCHAR(100),
  "division" VARCHAR(100),
  "conference" VARCHAR(100),
  "status" VARCHAR(100)
);
```

We use team_id as our primary key, which will be referenced by other tables in the future. We create our Players table next — foreign key references our Teams table.

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

We create final two tables, which I have listed below:


```sql
CREATE TABLE IF NOT EXISTS Games (
  "game_id" VARCHAR(100) PRIMARY KEY,
  "league_id" VARCHAR(100),
  "season"  INTEGER,
  "game_type" VARCHAR(100),
  "game_date" TIMESTAMP,
  "game_time" TIMESTAMP,
  "game_status" VARCHAR(100),
  "home_team_id" INTEGER,
  "away_team_id" INTEGER,
  "home_score" INTEGER,
  "away_score" INTEGER,
  "point_difference" INTEGER,
  FOREIGN KEY ("home_team_id") REFERENCES Teams("team_id"),
  FOREIGN KEY ("away_team_id") REFERENCES Teams("team_id")
);
```

```sql
CREATE TABLE IF NOT EXISTS Player_Stats (
  "player_id" INTEGER,
  "league_id"  INTEGER,
  "season" INTEGER,
  "game_type" VARCHAR(100),
  "games_played" INTEGER,
  "games_started" INTEGER,
  "minutes" INTEGER,
  "total_seconds" INTEGER,
  "fgm" INTEGER,
  "fga" INTEGER,
  "fg_pct" INTEGER,
  "2fgm" INTEGER,
  "2fga" INTEGER,
  "2fg_pct" INTEGER,
  "3fgm" INTEGER,
  "3fga" INTEGER,
  "3fg_pct" INTEGER,
  "ftm" INTEGER,
  "fta" INTEGER,
  "ft_pct" INTEGER,
  "oreb" INTEGER,
  "dreb" INTEGER,
  "reb" INTEGER,
  "ast" INTEGER,
  "tov" INTEGER,
  "stl" INTEGER,
  "blk" INTEGER,
  "blka" INTEGER,
  "pf" INTEGER,
  "techs" INTEGER,
  "plusminus" INTEGER,
  "pts" INTEGER,
  "pfd" INTEGER,
  PRIMARY KEY ("player_id", "total_seconds")
);
```

