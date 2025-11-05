from __future__ import annotations
import csv
from datetime import datetime, timedelta
from airflow import DAG
from airflow.sdk import task
from psycopg2 import Error as DatabaseError
from airflow.providers.postgres.hooks.postgres import PostgresHook
import os
import shutil


# --- Configuration ---
OUTPUT_DIR = "/opt/airflow/data"
# The final table name for the merged, cleaned data
TARGET_TABLE = "nba_stats_merged" 

default_args = {
    "owner": "IDS706",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

# Helper for column-name variations (kept for structure, but less necessary
# since your CSV headers are explicit)
def _pick(df, candidates, required=True):
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise KeyError(
            f"Expected one of {candidates} in columns: {list(df.columns)[:15]} ..."
        )
    return None


with DAG(
    dag_id="nba_pipeline", # Renamed DAG ID
    start_date=datetime(2025, 10, 1),
    schedule="@once",
    catchup=False,
    default_args=default_args,
) as dag:

    # 1) Players Data Cleaning
    @task()
    def clean_players(output_dir: str = OUTPUT_DIR) -> str:
        import pandas as pd
        path = "/opt/airflow/data/Players.csv"
        # Assuming your CSVs are named exactly as provided: Players, Games, Player_Stats, Teams
        df = pd.read_csv(path) 

        # Keep essential columns and clean 'jersey_number'
        keep_cols = [
            "player_id", "team_id", "league_id", "full_name", 
            "position_simple", "status", "jersey_number"
        ]
        df = df[keep_cols].drop_duplicates(subset=["player_id"], keep="last")
        
        # Basic cleaning for jersey_number (convert to int, coerce errors to NaN)
        df["jersey_number"] = pd.to_numeric(df["jersey_number"], errors="coerce").astype('Int64')

        out = os.path.join(output_dir, "players_clean.csv")
        df.to_csv(out, index=False)
        print(f"Players saved to {out} (rows={len(df)})")
        return out

    # 2) Teams Data Cleaning
    @task()
    def clean_teams(output_dir: str = OUTPUT_DIR) -> str:
        import pandas as pd
        path = "/opt/airflow/data/Teams.csv"
        df = pd.read_csv(path) 

        # Keep essential columns and ensure unique teams
        keep_cols = [
            "team_id", "league_id", "team_full_name", 
            "division", "conference", "status"
        ]
        df = df[keep_cols].drop_duplicates(subset=["team_id"], keep="last")

        out = os.path.join(output_dir, "teams_clean.csv")
        df.to_csv(out, index=False)
        print(f"Teams saved to {out} (rows={len(df)})")
        return out

    # 3) Games Data Cleaning (Simple clean, not used in final merge due to complexity)
    @task()
    def clean_games(output_dir: str = OUTPUT_DIR) -> str:
        import pandas as pd
        path = "/opt/airflow/data/Games.csv"
        df = pd.read_csv(path) 

        # Basic cleaning for scores and difference
        for col in ["home_score", "away_score", "point_difference"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Convert game_time to datetime
        df["game_time"] = pd.to_datetime(df["game_time"], errors="coerce")

        out = os.path.join(output_dir, "games_clean.csv")
        df.to_csv(out, index=False)
        print(f"Games saved to {out} (rows={len(df)})")
        return out

    # 4) Player Stats Data Cleaning
    @task()
    def clean_player_stats(output_dir: str = OUTPUT_DIR) -> str:
        import pandas as pd
        path = "/opt/airflow/data/Player_Stats.csv"
        df = pd.read_csv(path) 
        
        # Convert all numeric stats columns to numeric type
        numeric_cols = df.columns.drop(["player_id", "league_id", "season", "game_type"])
        for col in numeric_cols:
             df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Filter out rows with no minutes recorded (likely non-existent players or errors)
        df = df.dropna(subset=["minutes"])

        # Aggregate stats by player_id and season/game_type (to get a final summary per player)
        agg_cols = ["fgm", "fga", "pts", "reb", "ast", "minutes", "games_played"]
        agg = df.groupby(["player_id", "season", "game_type"], as_index=False)[agg_cols].sum()
        
        # Calculate a simple derived feature: Points Per Minute (PPM)
        agg["ppm"] = agg["pts"] / agg["minutes"].replace(0, 1) # Avoid division by zero

        out = os.path.join(output_dir, "player_stats_clean.csv")
        agg.to_csv(out, index=False)
        print(f"Player Stats saved to {out} (rows={len(agg)})")
        return out

    # 5) MERGE
    @task()
    def merge_stats_and_roster(
        players_path: str, teams_path: str, stats_path: str, output_dir: str = OUTPUT_DIR
    ) -> str:
        import pandas as pd

        players = pd.read_csv(players_path)
        teams = pd.read_csv(teams_path)
        stats = pd.read_csv(stats_path)
        
        # Merge Player Stats with Player info on player_id
        merged_stats_players = pd.merge(stats, players, on="player_id", how="left")

        # Merge the result with Team info on team_id
        # Note: We need to use specific columns from the 'teams' DataFrame to avoid
        # conflicts with player columns like 'status' or 'league_id'
        team_cols = ["team_id", "team_full_name", "division", "conference"]
        merged = pd.merge(
            merged_stats_players, teams[team_cols], on="team_id", how="left"
        )

        # Drop any remaining rows where the player or team info was missing
        merged = merged.dropna(subset=["full_name", "team_full_name"])

        # Final cleaning for numeric types
        numeric_cols = merged.columns.drop(["full_name", "team_full_name", "division", "conference"])
        for col in numeric_cols:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

        merged_path = os.path.join(output_dir, "merged_nba_data.csv")
        merged.to_csv(merged_path, index=False)
        print(f"Merged NBA data saved to {merged_path} (rows={len(merged)})")
        return merged_path

    # 6) LOAD TO POSTGRES (Modified for NBA columns and types)

    @task()
    def load_csv_to_pg(
        conn_id: str, csv_path: str, table: str = TARGET_TABLE, append: bool = False
    ) -> int:
        import pandas as pd
        from psycopg2 import Error as DatabaseError
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        
        df = pd.read_csv(csv_path)
        if df.empty:
            print("No rows to insert.")
            return 0
        
        # --- Preparation ---
        schema = "assignment"
        hook = PostgresHook(postgres_conn_id=conn_id)

        # Final check for numeric types
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        create_schema = f"CREATE SCHEMA IF NOT EXISTS {schema};"
        
        # SQL to define columns based on DataFrame types
        columns_sql = []
        for col in df.columns:
            if col in ["fgm", "fga", "pts", "reb", "ast", "minutes", "ppm", "jersey_number"]:
                columns_sql.append(f'"{col}" DOUBLE PRECISION')
            elif col in ["player_id", "team_id", "games_played"]:
                columns_sql.append(f'"{col}" INTEGER')
            else:
                columns_sql.append(f'"{col}" TEXT')

        create_table = f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table} (
                {', '.join(columns_sql)}
            );
        """
        delete_rows = f"DELETE FROM {schema}.{table};" if not append else None
        
        
        # --- MODIFICATION START: STEP 1 - CREATE AND COMMIT TABLE STRUCTURE ---
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_schema)
                    cur.execute(create_table)
                conn.commit() # IMMEDIATE COMMIT: Guarantees table exists.
            print(f"Schema and Table confirmed: {schema}.{table}")
        except Exception as e:
            # If this fails, it's a critical permission issue; re-raise the error.
            print(f"CRITICAL ERROR during schema/table creation: {e}")
            raise 
            
        # --- MODIFICATION END ---


        # --- STEP 2: LOAD DATA ---
        try:
            if delete_rows:
                # Use hook.run for DML (DELETE)
                hook.run(sql=delete_rows) 
                
            # Use hook.insert_rows for data loading
            hook.insert_rows(
                table=f'{schema}.{table}', 
                rows=df.to_records(index=False).tolist(), 
                target_fields=df.columns.tolist()
            )
            
            print(f"Inserted {len(df)} rows into {schema}.{table}")
            return len(df)
        except DatabaseError as e:
            print(f"Database error during insertion (data might be bad): {e}")
            return 0 # Fail gracefully on data error
        finally:
            # Note: insert_rows handles its own connection/cursor, so no final conn.close() here if using hook methods exclusively.
            pass


# --- Orchestration Remains the Same ---

# [players_file, teams_file, games_file, stats_file] >> merged_file >> load_to_database
# load_to_database >> [train_model, visualization] >> clean_folder_task


    # 7) SIMPLE ML MODEL (Modified to predict games_played from minutes)

    @task()
    def train_simple_model(conn_id: str, table: str = TARGET_TABLE) -> str:
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression # Changed to Linear Regression for numeric target
        from sklearn.metrics import mean_squared_error
        import joblib
        import numpy as np
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id=conn_id)
        # Predict games played (Y) based on total minutes (X)
        df = hook.get_pandas_df(
            f'SELECT "games_played", "minutes" FROM assignment."{table}";'
        )

        # Clean types
        df["games_played"] = pd.to_numeric(df["games_played"], errors="coerce")
        df["minutes"] = pd.to_numeric(df["minutes"], errors="coerce")

        # Drop NaNs
        df = df.replace([np.inf, -np.inf], np.nan).dropna(
            subset=["games_played", "minutes"]
        )

        # Define Target (Y) and Feature (X)
        y = df["games_played"]
        X = df[["minutes"]]

        if len(df) < 2:
             print("Not enough data to train model.")
             return "Model training skipped due to insufficient data."

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = LinearRegression() # Changed to Linear Regression
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds)) # Metric for Regression

        model_path = "/opt/airflow/data/simple_model.pkl"
        joblib.dump(model, model_path)

        print(f"Model trained with RMSE: {rmse:.2f}")
        return f"Model RMSE: {rmse:.2f}"

    # 8) VISUALIZATION (Modified for NBA stats: Avg Points by Division)

    @task()
    def perform_visualization(conn_id: str, table: str = TARGET_TABLE) -> str:
        import pandas as pd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id=conn_id)

        q = f"""
            SELECT "division","pts"
            FROM assignment."{table}";
        """

        df = hook.get_pandas_df(q)
        if df.empty:
            print("No data to plot.")
            return ""

        df["pts"] = pd.to_numeric(df["pts"], errors="coerce")
        df = df.dropna(subset=["pts", "division"])

        # Group + sort divisions by mean points
        summary = (
            df.groupby("division", as_index=False)["pts"]
            .agg(["mean", "count"])
            .reset_index()
            .sort_values("mean")
        )

        plt.figure(figsize=(12, 7))
        bars = plt.bar(summary["division"], summary["mean"], color="darkorange")
        

        # Add count labels above each bar
        for bar, n in zip(bars, summary["count"]):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"n={n}",
                ha="center",
                fontsize=10,
            )

        plt.title("Average Player Points (PTS) by Team Division", fontsize=16)
        plt.xlabel("Division", fontsize=12)
        plt.ylabel("Avg Player Points", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        img_path = "/opt/airflow/data/analysis_plot.png"
        plt.savefig(img_path)
        plt.close()

        print(f"Visualization saved to {img_path}")
        return img_path
    
    # --- Task Orchestration ---

    # Data Cleaning Tasks (all run in parallel initially)
    players_file = clean_players()
    teams_file = clean_teams()
    games_file = clean_games() # This is cleaned but not used in the final merge for simplicity
    stats_file = clean_player_stats()

    # Merge Task (depends on players, teams, and stats being cleaned)
    merged_file = merge_stats_and_roster(
        players_path=players_file, 
        teams_path=teams_file, 
        stats_path=stats_file
    )

    # Load to Database (depends on the final merged file)
    load_to_database = load_csv_to_pg(
        conn_id="Postgres", csv_path=merged_file, table=TARGET_TABLE
    )
    
    # Analysis Tasks (depend on the data being loaded to the database)
    train_model = train_simple_model(conn_id="Postgres", table=TARGET_TABLE)
    visualization = perform_visualization(conn_id="Postgres", table=TARGET_TABLE)
    
    # # Cleanup Task (runs last)
    # #clean_folder_task = clear_folder(folder_path=OUTPUT_DIR)

    # # Define Dependencies
    # load_to_database >> [train_model, visualization] >> clean_folder_task
    
    # # Ensure the merge waits for all cleaning tasks
    # [players_file, teams_file, games_file, stats_file] >> merged_file >> load_to_database