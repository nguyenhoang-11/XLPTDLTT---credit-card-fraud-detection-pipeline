"""Kafka producer that streams credit card transactions from CSV into Kafka."""
import csv
import json
import random
import time
from datetime import datetime
from pathlib import Path
import os

from kafka import KafkaProducer


BASE_DIR = Path(__file__).resolve().parent.parent
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC_NAME = "credit_card_transactions"
CSV_FILE_PATH = BASE_DIR / "data" / "User0_credit_card_transactions.csv"


def create_producer():
    """Create a Kafka producer with JSON serialization."""
    max_retries = 20
    wait_seconds = 10
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Producer] Attempt {attempt}/{max_retries} - Trying to connect to Kafka broker at {KAFKA_BROKER}...")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda v: json.dumps(v).encode("utf-8") if v else None,
                acks="all",
                retries=3,
            )
            print(f"[Producer] Connected to Kafka broker: {KAFKA_BROKER}")
            return producer
        except Exception as exc:
                print(f"[Producer] Attempt {attempt}/{max_retries} - Failed to connect to Kafka: {exc}")
            if attempt < max_retries:
                print(f"[Producer] Waiting {wait_seconds} seconds before retrying...")
                time.sleep(wait_seconds)
            else:
                print("[Producer] Exceeded maximum retry attempts. Exiting.")
                return None


def read_and_send_csv(producer: KafkaProducer) -> None:
    """Read the CSV row by row and send each record to Kafka with a random delay."""
    try:
        if not CSV_FILE_PATH.exists():
            print(f"Error: CSV file not found: {CSV_FILE_PATH}")
            return
        
        with CSV_FILE_PATH.open("r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            if not csv_reader:
                print("Error: CSV file is empty or invalid")
                return
            
            count = 0

            for row in csv_reader:
                row["processing_timestamp"] = datetime.now().isoformat()
                row["record_id"] = count

                key = str(row.get("User", "0"))

                future = producer.send(
                    TOPIC_NAME,
                    key=key,
                    value=row,
                )

                try:
                    record_metadata = future.get(timeout=10)
                except Exception as send_exc:
                    print(f"Failed to send record #{count}: {send_exc}")
                    continue

                count += 1

                print(
                    f"Record #{count} | Partition: {record_metadata.partition} | Offset: {record_metadata.offset} | "
                    f"User: {row['User']} | Amount: {row['Amount']} | Fraud: {row['Is Fraud?']}"
                )

                time.sleep(random.uniform(1, 5))

    except FileNotFoundError:
        print(f"CSV file not found: {CSV_FILE_PATH}")
    except Exception as exc:  # pragma: no cover - runtime logging only
        print(f"Unexpected error: {exc}")
    finally:
        if producer:
            producer.flush()
            producer.close()
            print("Closed Kafka producer.")


def main():
    producer = create_producer()

    if producer:
        read_and_send_csv(producer)
    else:
        print("Unable to start producer. Please verify the Kafka server.")


if __name__ == "__main__":
    main()