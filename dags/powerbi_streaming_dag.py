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
    schedule_interval='*/5 * * * *',  # Run every 5 minutes
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
        tracking_file = "/app/powerbi_exports/last_push_timestamp.txt"
        last_timestamp = None

        if os.path.exists(tracking_file):
            with open(tracking_file, 'r') as f:
                last_timestamp = f.read().strip()
            print(f"Last push timestamp: {last_timestamp}")
            # Only get new records since last push
            df = df.filter(col('transaction_datetime') > last_timestamp)

        total = df.count()
        print(f"New records to push: {total:,}")

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

        # Select 15 most important columns for 10 research questions
        columns_to_select = [
            'transaction_datetime', 'Amount_USD', 'Amount_VND',
            'Merchant Name', 'Merchant City', 'Merchant State',
            'MCC', 'Is Fraud?', 'transaction_type',
            'day_of_week', 'transaction_year', 'transaction_month', 'transaction_hour',
            'User', 'Card'
        ]
        df_filtered = df_pd[columns_to_select].copy()

        # Rename columns to match Power BI schema (no spaces, no special chars)
        df_filtered.columns = [
            'transaction_datetime', 'Amount_USD', 'Amount_VND',
            'Merchant_Name', 'Merchant_City', 'Merchant_State',
            'MCC', 'Is_Fraud', 'transaction_type',
            'day_of_week', 'transaction_year', 'transaction_month', 'transaction_hour',
            'User', 'Card'
        ]

        print(f"Pushing {len(df_filtered):,} rows with 15 columns to Power BI...")

        # Replace NaN, Inf, -Inf with None (null in JSON)
        df_filtered = df_filtered.replace([np.nan, np.inf, -np.inf], None)

        # Convert to list of dicts
        rows = df_filtered.to_dict('records')

        # Fix timestamp format for Power BI
        for row in rows:
            if 'timestamp' in row and isinstance(row['timestamp'], str):
                if 'T' not in row['timestamp']:
                    row['timestamp'] = row['timestamp'].replace(' ', 'T') + '.000Z'

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

        # Update last processed timestamp
        max_timestamp = df_filtered['transaction_datetime'].max()
        with open(tracking_file, 'w') as f:
            f.write(str(max_timestamp))
        print(f"Updated tracking file with timestamp: {max_timestamp}")

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
