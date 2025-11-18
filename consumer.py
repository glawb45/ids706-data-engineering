import json
import psycopg2
from kafka import KafkaConsumer

def run_consumer():
    """Consumes trip messages from Kafka and inserts them into PostgreSQL."""
    try:
        print("[Consumer] Connecting to Kafka at localhost:9092...")
        consumer = KafkaConsumer(
            "rideshare_trips",
            bootstrap_servers="localhost:9092",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            group_id="rideshare-consumer-group",
        )
        print("[Consumer] ✓ Connected to Kafka successfully!")
        
        print("[Consumer] Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            dbname="kafka_db",
            user="kafka_user",
            password="kafka_password",
            host="localhost",
            port="5432",
        )
        conn.autocommit = True
        cur = conn.cursor()
        print("[Consumer] ✓ Connected to PostgreSQL successfully!")
        
        # Create trips table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trips (
                trip_id VARCHAR(50) PRIMARY KEY,
                driver_id VARCHAR(50),
                passenger_id VARCHAR(50),
                timestamp TIMESTAMP,
                pickup_lat NUMERIC(10, 6),
                pickup_lon NUMERIC(10, 6),
                dropoff_lat NUMERIC(10, 6),
                dropoff_lon NUMERIC(10, 6),
                city VARCHAR(100),
                distance_km NUMERIC(10, 2),
                duration_minutes INTEGER,
                fare NUMERIC(10, 2),
                surge_multiplier NUMERIC(4, 2),
                vehicle_type VARCHAR(50),
                payment_method VARCHAR(50),
                rating NUMERIC(3, 1),
                status VARCHAR(50)
            );
            """
        )
        print("[Consumer] ✓ Table 'trips' ready.")
        
        print("[Consumer] 🎧 Listening for trip messages...\n")
        
        message_count = 0
        for message in consumer:
            try:
                trip_data = message.value
                
                insert_query = """
                    INSERT INTO trips (
                        trip_id, driver_id, passenger_id, timestamp,
                        pickup_lat, pickup_lon, dropoff_lat, dropoff_lon,
                        city, distance_km, duration_minutes, fare,
                        surge_multiplier, vehicle_type, payment_method,
                        rating, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (trip_id) DO NOTHING;
                """
                
                cur.execute(
                    insert_query,
                    (
                        trip_data["trip_id"],
                        trip_data["driver_id"],
                        trip_data["passenger_id"],
                        trip_data["timestamp"],
                        trip_data["pickup_location"]["lat"],
                        trip_data["pickup_location"]["lon"],
                        trip_data["dropoff_location"]["lat"],
                        trip_data["dropoff_location"]["lon"],
                        trip_data["city"],
                        trip_data["distance_km"],
                        trip_data["duration_minutes"],
                        trip_data["fare"],
                        trip_data["surge_multiplier"],
                        trip_data["vehicle_type"],
                        trip_data["payment_method"],
                        trip_data["rating"],
                        trip_data["status"],
                    ),
                )
                
                message_count += 1
                print(f"[Consumer] ✓ #{message_count} Inserted trip {trip_data['trip_id']} | "
                      f"{trip_data['city']} | {trip_data['distance_km']}km | "
                      f"${trip_data['fare']} | {trip_data['status']}")
                
            except Exception as e:
                print(f"[Consumer ERROR] Failed to process message: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n[Consumer] Shutting down gracefully...")
    except Exception as e:
        print(f"[Consumer ERROR] {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_consumer()