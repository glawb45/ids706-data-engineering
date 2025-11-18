import time
import json
import uuid
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
from faker import Faker

fake = Faker()

def generate_synthetic_trip():
    """Generates synthetic ride-sharing trip data."""
    
    # Trip status options
    statuses = ["requested", "accepted", "in_progress", "completed", "cancelled"]
    
    # Cities and their coordinates
    cities = {
        "New York": {"lat_range": (40.70, 40.80), "lon_range": (-74.02, -73.90)},
        "Los Angeles": {"lat_range": (34.00, 34.15), "lon_range": (-118.50, -118.20)},
        "Chicago": {"lat_range": (41.85, 41.95), "lon_range": (-87.70, -87.60)},
        "San Francisco": {"lat_range": (37.70, 37.80), "lon_range": (-122.50, -122.40)},
        "Miami": {"lat_range": (25.75, 25.85), "lon_range": (-80.25, -80.15)},
    }
    
    # Vehicle types
    vehicle_types = ["Economy", "Comfort", "Premium", "XL", "Electric"]
    
    # Payment methods
    payment_methods = ["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Cash"]
    
    # Select random city
    city = random.choice(list(cities.keys()))
    city_data = cities[city]
    
    # Generate pickup and dropoff locations
    pickup_lat = round(random.uniform(*city_data["lat_range"]), 6)
    pickup_lon = round(random.uniform(*city_data["lon_range"]), 6)
    dropoff_lat = round(random.uniform(*city_data["lat_range"]), 6)
    dropoff_lon = round(random.uniform(*city_data["lon_range"]), 6)
    
    # Generate trip metrics
    distance_km = round(random.uniform(1.0, 25.0), 2)
    duration_minutes = int(distance_km * random.uniform(2, 5))  # Roughly 2-5 min per km
    base_fare = distance_km * random.uniform(1.5, 3.0)
    surge_multiplier = random.choice([1.0, 1.0, 1.0, 1.2, 1.5, 2.0])  # Surge pricing
    fare = round(base_fare * surge_multiplier, 2)
    
    # Driver rating
    rating = round(random.uniform(3.5, 5.0), 1)
    
    # Status
    status = random.choice(statuses)
    
    # Vehicle type
    vehicle_type = random.choice(vehicle_types)
    
    # Payment method
    payment_method = random.choice(payment_methods)
    
    # Timestamp
    timestamp = datetime.now()
    
    return {
        "trip_id": str(uuid.uuid4())[:8],
        "driver_id": f"DRV{random.randint(1000, 9999)}",
        "passenger_id": f"PSG{random.randint(1000, 9999)}",
        "timestamp": timestamp.isoformat(),
        "pickup_location": {
            "lat": pickup_lat,
            "lon": pickup_lon
        },
        "dropoff_location": {
            "lat": dropoff_lat,
            "lon": dropoff_lon
        },
        "city": city,
        "distance_km": distance_km,
        "duration_minutes": duration_minutes,
        "fare": fare,
        "surge_multiplier": surge_multiplier,
        "vehicle_type": vehicle_type,
        "payment_method": payment_method,
        "rating": rating,
        "status": status,
    }

def run_producer():
    """Kafka producer that sends synthetic trips to the 'rideshare_trips' topic."""
    try:
        print("[Producer] Connecting to Kafka at localhost:9092...")
        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=30000,
            max_block_ms=60000,
            retries=5,
        )
        print("[Producer] ✓ Connected to Kafka successfully!")
        
        count = 0
        while True:
            trip = generate_synthetic_trip()
            print(f"\n[Producer] Sending trip #{count}:")
            print(f"  Trip ID: {trip['trip_id']}")
            print(f"  City: {trip['city']}")
            print(f"  Distance: {trip['distance_km']} km")
            print(f"  Fare: ${trip['fare']}")
            print(f"  Status: {trip['status']}")
            
            future = producer.send("rideshare_trips", value=trip)
            record_metadata = future.get(timeout=10)
            print(f"[Producer] ✓ Sent to partition {record_metadata.partition} at offset {record_metadata.offset}")
            
            producer.flush()
            count += 1
            
            # Random delay between trips (0.5 to 2 seconds)
            sleep_time = random.uniform(0.5, 2.0)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n[Producer] Shutting down gracefully...")
    except Exception as e:
        print(f"[Producer ERROR] {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_producer()