# Apache Kafka

## Goals
This project dives into real-time streaming in a data pipeline. We will use sample data to further generate synthetic data.

The main objective of this project is to utilize Apache Kafka as a workflow to build a real-time streaming dashboard and platform.

This project demonstrates a **real-time data streaming pipeline** that:

- Generates synthetic e-commerce orders
- Streams them through Apache Kafka
- Stores them in PostgreSQL
- Visualizes them in a live dashboard

By the end of this guide, you'll have:

**Producer**: Generates fake orders every 0.5-2 seconds

**Kafka**: Message broker that handles the data stream

**Consumer**: Reads orders from Kafka and saves to database

**PostgreSQL**: Stores all order data

**Streamlit Dashboard**: Real-time visualization with charts and KPIs

**Live Dashboard Preview:**

- Total orders, sales value, conversion rates
- Sales by category, city, payment method
- Time-series trends
- Auto-refreshing every 5 seconds

This is what our workflow will look like:

```bash
kafka_realtime_pipeline/
├── docker-compose.yml
├── requirements.txt
├── producer.py
├── consumer.py
└── dashboard.py
```

## Producers

We want to continuously generate and stream synthetic ride-sharing trip data. This file uses libraries like faker and random to create realistic, mock data points, including a unique trip ID, driver and passenger IDs, pickup/dropoff coordinates across five major cities (New York, LA, Chicago, San Francisco, Miami), distance, duration, fare (calculated with a potential surge multiplier), vehicle type, and current trip status. This data is structured into a Python dictionary and then converted to a JSON string.

The script's main loop, orchestrated by the run_producer function, connects to a Kafka broker running on localhost:9092. Once connected, it enters an infinite loop where it calls the generate_synthetic_trip function to create a new record. It then serializes the trip data to JSON, sends it to the Kafka topic named rideshare_trips, prints the details and the Kafka offset for confirmation, and introduces a random delay (0.5 to 2.0 seconds) before sending the next message. The primary purpose of this file is to simulate a live stream of transactional data, which is a common task in data engineering and streaming pipeline development.

## Consumers

This is the Kafka Consumer, serving as the final stage in a data streaming pipeline to ensure data persistence . Its primary function is to establish two crucial connections: one to the Kafka cluster to read incoming data from the rideshare_trips topic, and another to the PostgreSQL database to store the processed records. After connecting, the script immediately prepares the database by creating the trips table, ensuring it can accommodate all the detailed fields of the ride-share data, such as trip identifiers, locations, fares, and status.

The script then enters a continuous loop, actively listening for messages on the Kafka topic. When a message arrives, it deserializes the JSON-formatted data and executes a parameterized SQL INSERT statement to load the record into the PostgreSQL trips table. The intention is to demonstrate the Extract and Load (EL) portion of a streaming ETL process: safely consuming real-time events from an intermediary message broker (Kafka) and persisting them into a reliable relational database (PostgreSQL) for subsequent analytical use or reporting.

## Dashboard







