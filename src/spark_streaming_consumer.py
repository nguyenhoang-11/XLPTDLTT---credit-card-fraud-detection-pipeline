
"""Spark Structured Streaming consumer for credit card transactions."""
from datetime import datetime
from pathlib import Path
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    concat,
    count,
    current_date,
    current_timestamp,
    date_format,
    dayofweek,
    from_json,
    hour,
    lit,
    regexp_replace,
    sum,
    to_timestamp,
    udf,
    when,
    window,
    day,
    month,
    year,
)
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

from .exchange_rate_scraper import ExchangeRateScraper


BASE_DIR = Path(__file__).resolve().parent.parent

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = "credit_card_transactions"
CHECKPOINT_DIR = BASE_DIR / "checkpoint"
OUTPUT_DIR = BASE_DIR / "output"

# Optional HDFS URIs (set via environment when using Hadoop)
OUTPUT_URI = os.getenv("OUTPUT_URI")
CHECKPOINT_URI = os.getenv("CHECKPOINT_URI")

schema = StructType(
    [
        StructField("User", StringType(), True),
        StructField("Card", StringType(), True),
        StructField("Year", StringType(), True),
        StructField("Month", StringType(), True),
        StructField("Day", StringType(), True),
        StructField("Time", StringType(), True),
        StructField("Amount", StringType(), True),
        StructField("Use Chip", StringType(), True),
        StructField("Merchant Name", StringType(), True),
        StructField("Merchant City", StringType(), True),
        StructField("Merchant State", StringType(), True),
        StructField("Zip", StringType(), True),
        StructField("MCC", StringType(), True),
        StructField("Errors?", StringType(), True),
        StructField("Is Fraud?", StringType(), True),
        StructField("processing_timestamp", StringType(), True),
        StructField("record_id", StringType(), True),
    ]
)


def create_spark_session():
    """Create a Spark session configured for Kafka streaming."""
    spark = (
        SparkSession.builder.appName("CreditCardTransactionStreaming")
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
        .config(
            "spark.sql.streaming.checkpointLocation",
            CHECKPOINT_URI if CHECKPOINT_URI else str(CHECKPOINT_DIR),
        )
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )

    # If provided, set default FS to HDFS (or other) so Spark writes to it
    fs_default = os.getenv("FS_DEFAULTFS")
    if fs_default:
        spark.sparkContext._jsc.hadoopConfiguration().set("fs.defaultFS", fs_default)
        spark.conf.set("spark.hadoop.fs.defaultFS", fs_default)

    spark.sparkContext.setLogLevel("WARN")
    return spark


def get_exchange_rate_udf():
    """Return a UDF that fetches the USD/VND rate with one-hour caching."""
    cached_rate = {"rate": None, "timestamp": None}

    def fetch_rate():
        now = datetime.now()

        if cached_rate["rate"] and cached_rate["timestamp"]:
            time_diff = (now - cached_rate["timestamp"]).total_seconds()
            if time_diff < 3600:
                return cached_rate["rate"]

        try:
            scraper = ExchangeRateScraper()
            usd_rate = scraper.get_usd_rate()
            if usd_rate and usd_rate.get("transfer"):
                rate = usd_rate["transfer"]
                cached_rate["rate"] = rate
                cached_rate["timestamp"] = now
                print(f"Updated exchange rate: 1 USD = {rate:,.0f} VND")
                return float(rate)
        except Exception as exc:  # pragma: no cover - external dependency
            print(f"Exchange rate lookup failed: {exc}")

        return 24000.0

    return udf(fetch_rate, DoubleType())


def get_exchange_rate_broadcast(spark: SparkSession) -> float:
    """Fetch USD/VND rate once and return as broadcast value.
    
    This is more efficient than UDF which would call API for every partition.
    """
    try:
        scraper = ExchangeRateScraper()
        usd_rate = scraper.get_usd_rate()
        if usd_rate and usd_rate.get("transfer"):
            rate = float(usd_rate["transfer"])
            print(f"Fetched exchange rate: 1 USD = {rate:,.0f} VND")
            return rate
    except Exception as exc:  # pragma: no cover - external dependency
        print(f"Exchange rate lookup failed: {exc}")
    
    return 24000.0


def process_stream(spark: SparkSession):
    """Consume the Kafka stream, enrich, and write to multiple sinks."""

    print("=" * 80)
    print("SPARK STREAMING - CREDIT CARD TRANSACTION PROCESSING")
    print("=" * 80)
    print(f"Connecting to Kafka: {KAFKA_BROKER}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(
        f"Checkpoint: "
        + (CHECKPOINT_URI if CHECKPOINT_URI else str(CHECKPOINT_DIR))
    )
    print(f"Output: " + (OUTPUT_URI if OUTPUT_URI else str(OUTPUT_DIR)))
    print("=" * 80)

    df_stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .option("kafka.session.timeout.ms", "30000")
        .option("kafka.request.timeout.ms", "40000")
        .load()
    )

    df_parsed = df_stream.select(
        col("key").cast("string").alias("key"),
        from_json(col("value").cast("string"), schema).alias("data"),
        col("timestamp").alias("kafka_timestamp"),
    ).select("key", "data.*", "kafka_timestamp")

    df_cleaned = df_parsed.withColumn("Amount_USD", regexp_replace(col("Amount"), "\\$", "").cast("double"))

    # Fetch exchange rate once at startup (broadcast to all executors)
    exchange_rate = get_exchange_rate_broadcast(spark)
    df_with_rate = df_cleaned.withColumn("exchange_rate", lit(exchange_rate))
    df_with_rate = df_with_rate.withColumn("Amount_VND", col("Amount_USD") * col("exchange_rate"))

    df_with_date = df_with_rate.withColumn(
        "transaction_datetime",
        to_timestamp(
            concat(col("Year"), lit("-"), col("Month"), lit("-"), col("Day"), lit(" "), col("Time")),
            "yyyy-M-d HH:mm",
        ),
    )

    # Format date and time columns as required (dd/mm/yyyy and hh:mm:ss)
    df_with_formatted_date = (
        df_with_date
        .withColumn("transaction_date", date_format(col("transaction_datetime"), "dd/MM/yyyy"))
        .withColumn("transaction_time", date_format(col("transaction_datetime"), "HH:mm:ss"))
        # Add analysis columns
        .withColumn("transaction_year", year(col("transaction_datetime")))
        .withColumn("transaction_month", month(col("transaction_datetime")))
        .withColumn("transaction_day", day(col("transaction_datetime")))
        .withColumn("transaction_hour", hour(col("transaction_datetime")))
        .withColumn("day_of_week", dayofweek(col("transaction_datetime")))
    )

    df_categorized = df_with_formatted_date.withColumn(
        "transaction_type",
        when(col("Is Fraud?") == "Yes", "FRAUD")
        .when(col("Amount_USD") > 500, "HIGH_VALUE")
        .when(col("Amount_USD") > 100, "MEDIUM_VALUE")
        .otherwise("LOW_VALUE"),
    )

    # Add helper columns for Power BI analysis (replace DAX calculations)
    df_with_helpers = df_categorized\
        .withColumn("is_high_value", when(col("Amount_USD") > 500, 1).otherwise(0))\
        .withColumn("is_fraud_flag", when(col("Is Fraud?") == "Yes", 1).otherwise(0))\
        .withColumn("is_weekday", when(col("day_of_week").isin([2, 3, 4, 5, 6]), 1).otherwise(0))\
        .withColumn("is_weekend", when(col("day_of_week").isin([1, 7]), 1).otherwise(0))

    # Filter out transactions with errors AND fraud (YÊU CẦU CỦA THẦY)
    # "Errors?" = technical errors that should be filtered out
    # "Is Fraud? = Yes" = fraud transactions, NOT successful, do NOT process further
    df_filtered = df_with_helpers.filter(
        (((col("Errors?").isNull()) | (col("Errors?") == "")) &
         ((col("Is Fraud?").isNull()) | (col("Is Fraud?") == "") | (col("Is Fraud?") == "No")))
    )

    # Deduplication is handled by Airflow tracking to avoid re-pushing on restart
    df_final = df_filtered.withColumn("processed_at", current_timestamp()).withColumn("processing_date", current_date())

    df_output = df_final.select(
        "User",
        "Card",
        "transaction_datetime",
        "transaction_year",
        "transaction_month",
        "transaction_day",
        "transaction_hour",
        "day_of_week",
        "Amount_USD",
        "Amount_VND",
        "Merchant Name",
        "Merchant City",
        "Merchant State",
        "MCC",
        "Is Fraud?",
        "transaction_type",
        "is_high_value",
        "is_fraud_flag",
        "is_weekday",
        "is_weekend",
        "processed_at",
    )

    # Create local directories only when not using HDFS
    if OUTPUT_URI is None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if CHECKPOINT_URI is None:
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    # Path for transactions data (no partitioning for easier Power BI access)
    transactions_path = (OUTPUT_URI + "/transactions") if OUTPUT_URI else str(OUTPUT_DIR / "transactions")
    transactions_ckpt = (
        (CHECKPOINT_URI + "/transactions") if CHECKPOINT_URI else str(CHECKPOINT_DIR / "transactions")
    )

    query_transactions = (
        df_output.writeStream.outputMode("append")
        .format("csv")
        .option("path", transactions_path)
        .option("checkpointLocation", transactions_ckpt)
        .option("header", "true")
        .trigger(processingTime="30 seconds")
        .start()
    )

    print("\nStreaming queries started:")
    print("  - Transactions (CSV to HDFS/Local)")
    print("\nProcessing stream... Press Ctrl+C to stop.")

    spark.streams.awaitAnyTermination()

    if query_transactions.isActive:
        query_transactions.stop()


def main():
    try:
        spark = create_spark_session()
        process_stream(spark)

    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        import traceback

        traceback.print_exc()
    finally:
        print("Stream processor terminated.")


if __name__ == "__main__":
    main()