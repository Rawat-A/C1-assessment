# Purpose: Shared Bronze CSV-to-Delta ingestion helper.
# Inputs:  SparkSession, CSV path, Delta output path, entity name.
# Outputs: Row count written; Delta table on disk.

"""Bronze ingestion utilities."""

from datetime import datetime

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import current_timestamp


def ingest_csv_to_delta(
    spark: SparkSession,
    csv_path: str,
    delta_path: str,
    entity_name: str,
) -> int:
    """Read a raw CSV and write it to a Bronze Delta table with an ingest timestamp.

    Args:
        spark: Active SparkSession.
        csv_path: Source CSV path (local or DBFS).
        delta_path: Target Delta table path.
        entity_name: Label used in log messages.

    Returns:
        Number of rows ingested.
    """
    df: DataFrame = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(csv_path)
    )
    df = df.withColumn("_ingest_timestamp", current_timestamp())
    row_count: int = df.count()
    df.write.format("delta").mode("overwrite").save(delta_path)
    print(
        f"[Bronze] {entity_name}: ingested {row_count} rows "
        f"at {datetime.utcnow().isoformat()}Z -> {delta_path}"
    )
    return row_count
