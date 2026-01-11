"""
Airflow DAG: Push data to Power BI Streaming Dataset

This DAG:
1. Exports transaction data from HDFS to CSV using PySpark
2. Pushes data to Power BI Streaming Dataset via REST API
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import os
import sys


default_args = {
    'owner': 'credit-pipeline',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

dag = DAG(
    'powerbi_streaming_upload',
    default_args=default_args,
    description='Push data to Power BI Streaming Dataset',
    schedule_interval='*/2 * * * *',  # Run every 2 minutes for demo
    catchup=False,
    tags=['powerbi', 'streaming'],
)


def export_and_push(**context):
    """Export from HDFS and push to Power BI Streaming API"""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col
    import requests
    import json

    print("=== STEP 1: Export CSV from HDFS ===")

    # Create Spark session
    spark = SparkSession.builder \
        .appName("ExportToStreaming") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try:
        # Read from HDFS
        hdfs_path = "hdfs://namenode:9000/user/credit-pipeline/output/transactions"
        print(f"Reading from HDFS: {hdfs_path}")

        df = spark.read.csv(hdfs_path, header=True, inferSchema=True)

        # Track last processed timestamp to avoid duplicates
        # Using processed_at (Spark's timestamp) instead of transaction_datetime (CSV has old 2003 dates)
        tracking_file = "/app/powerbi_exports/last_push_timestamp.txt"
        last_timestamp = None

        if os.path.exists(tracking_file):
            with open(tracking_file, 'r') as f:
                last_timestamp = f.read().strip()
            print(f"Last push timestamp (processed_at): {last_timestamp}")
            # Only get new records since last push - filter by processed_at
            df = df.filter(col('processed_at') > last_timestamp)
        else:
            print("No tracking file found - this is the first push")

        total = df.count()
        print(f"Total NEW records to push: {total:,}")

        if total == 0:
            print("No new data to push. Skipping...")
            spark.stop()
            return "No new data"

        # Export to CSV
        output_file = "/app/powerbi_exports/all_transactions.csv"
        temp_dir = "/tmp/spark_csv_streaming"

        df.coalesce(1).write.mode("overwrite").option("header", True).csv(temp_dir)

        import glob, shutil
        csv_files = glob.glob(f"{temp_dir}/part-*.csv")
        if csv_files:
            # Copy file content only (no permissions)
            with open(csv_files[0], 'rb') as src, open(output_file, 'wb') as dst:
                dst.write(src.read())
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Exported to: {output_file}")
        else:
            raise Exception("No CSV file generated")

        spark.stop()

        print("\n=== STEP 2: Push to Power BI Streaming API ===")

        # Get streaming URL
        streaming_url = os.getenv('POWERBI_STREAMING_URL')
        if not streaming_url:
            raise Exception("Missing POWERBI_STREAMING_URL environment variable")

        # Read CSV and push
        import pandas as pd
        import numpy as np
        df_pd = pd.read_csv(output_file)

        print(f"Total rows in CSV: {len(df_pd):,}")

        # Select 19 columns including helper columns for analysis (replaces DAX)
        columns_to_select = [
            'transaction_datetime', 'Amount_USD', 'Amount_VND',
            'Merchant Name', 'Merchant City', 'Merchant State',
            'MCC', 'Is Fraud?', 'transaction_type',
            'day_of_week', 'transaction_year', 'transaction_month', 'transaction_hour',
            'User', 'Card',
            'is_high_value', 'is_fraud_flag', 'is_weekday', 'is_weekend'
        ]
        df_filtered = df_pd[columns_to_select].copy()

        # Rename columns to match Power BI schema (no spaces, no special chars)
        df_filtered.columns = [
            'transaction_datetime', 'Amount_USD', 'Amount_VND',
            'Merchant_Name', 'Merchant_City', 'Merchant_State',
            'MCC', 'Is_Fraud', 'transaction_type',
            'day_of_week', 'transaction_year', 'transaction_month', 'transaction_hour',
            'User', 'Card',
            'is_high_value', 'is_fraud_flag', 'is_weekday', 'is_weekend'
        ]

        print(f"Pushing {len(df_filtered):,} rows with 19 columns to Power BI...")

        # Replace NaN, Inf, -Inf with None (null in JSON)
        df_filtered = df_filtered.replace([np.nan, np.inf, -np.inf], None)

        # Convert to list of dicts
        rows = df_filtered.to_dict('records')

        # Fix timestamp format for Power BI (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ)
        for row in rows:
            if 'transaction_datetime' in row and row['transaction_datetime'] is not None:
                # Convert to string if it's a pandas Timestamp
                if hasattr(row['transaction_datetime'], 'isoformat'):
                    row['transaction_datetime'] = row['transaction_datetime'].isoformat() + 'Z'
                elif isinstance(row['transaction_datetime'], str):
                    # If already string, ensure ISO 8601 format
                    if 'T' not in row['transaction_datetime']:
                        row['transaction_datetime'] = row['transaction_datetime'].replace(' ', 'T') + 'Z'
                    elif not row['transaction_datetime'].endswith('Z'):
                        row['transaction_datetime'] = row['transaction_datetime'] + 'Z'

        # Push in batches of 1000
        batch_size = 1000
        total_batches = (len(rows) + batch_size - 1) // batch_size

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            batch_num = i // batch_size + 1

            print(f"Batch {batch_num}/{total_batches} ({len(batch)} rows)...", end=" ")

            response = requests.post(
                streaming_url,
                headers={'Content-Type': 'application/json'},
                json=batch,
                timeout=30
            )
            response.raise_for_status()
            print("OK")

        print(f"\nSUCCESS: Pushed {len(rows):,} rows to Power BI Streaming Dataset")

        # Update last processed timestamp - use processed_at from Spark
        max_timestamp = df_pd['processed_at'].max()
        with open(tracking_file, 'w') as f:
            f.write(str(max_timestamp))
        print(f"Updated tracking file with processed_at timestamp: {max_timestamp}")

        return f"Pushed {len(rows):,} rows"

    except Exception as e:
        print(f"ERROR: {e}")
        raise


task_push_streaming = PythonOperator(
    task_id='export_and_push_streaming',
    python_callable=export_and_push,
    provide_context=True,
    dag=dag,
)
