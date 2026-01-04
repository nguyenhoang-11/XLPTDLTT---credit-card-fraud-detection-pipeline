
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

    get_rate = get_exchange_rate_udf()
    df_with_rate = df_cleaned.withColumn("exchange_rate", get_rate())
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

    # Filter out transactions with errors OR fraud (as per requirements)
    # "Is Fraud = Yes xác định lỗi và giao dịch này xem như không thành công, không cần xử lý tiếp"
    df_filtered = df_categorized.filter(
        ((col("Errors?").isNull()) | (col("Errors?") == "")) &
        ((col("Is Fraud?") == "No") | (col("Is Fraud?").isNull()))
    )

    # Add watermark for deduplication (allow 24 hours late data to handle loop mode)
    df_watermarked = df_filtered.withWatermark("transaction_datetime", "24 hours")

    # Remove duplicates based on unique transaction key within watermark window
    # A transaction is unique by: transaction_datetime + User + Card + Amount_USD
    # Using dropDuplicatesWithinWatermark to maintain state efficiently
    df_deduplicated = df_watermarked.dropDuplicates([
        "transaction_datetime", "User", "Card", "Amount_USD"
    ])

    df_final = df_deduplicated.withColumn("processed_at", current_timestamp()).withColumn("processing_date", current_date())

    df_output = df_final.select(
        "User",
        "Card",
        "transaction_date",
        "transaction_time",
        "transaction_datetime",
        "transaction_year",
        "transaction_month",
        "transaction_day",
        "transaction_hour",
        "day_of_week",
        "Amount",
        "Amount_USD",
        "Amount_VND",
        "exchange_rate",
        "Use Chip",
        "Merchant Name",
        "Merchant City",
        "Merchant State",
        "Zip",
        "MCC",
        "Is Fraud?",
        "transaction_type",
        "processed_at",
        "processing_date",
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

    query_console = (
        df_output.writeStream.outputMode("append")
        .format("console")
        .option("truncate", "false")
        .trigger(processingTime="30 seconds")
        .start()
    )

    df_user_stats = df_output.groupBy(window(col("processed_at"), "1 minute"), col("User")).agg(
        count("*").alias("transaction_count"),
        sum("Amount_VND").alias("total_amount_vnd"),
        avg("Amount_VND").alias("avg_amount_vnd"),
        sum(when(col("Is Fraud?") == "Yes", 1).otherwise(0)).alias("fraud_count"),
    )

    query_stats = (
        df_user_stats.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .trigger(processingTime="1 minute")
        .queryName("user_statistics")
        .start()
    )

    print("\nStreaming queries started:")
    print("  - Transactions (CSV)")
    print("  - Console monitoring")
    print("  - User statistics")
    print("\nProcessing stream... Press Ctrl+C to stop.")

    spark.streams.awaitAnyTermination()

    for query in [query_transactions, query_console, query_stats]:
        if query.isActive:
            query.stop()


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