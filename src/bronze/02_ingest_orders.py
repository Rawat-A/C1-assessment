# Purpose: Ingest orders.csv from local/DBFS into Bronze Delta (raw, no transforms).
# Inputs:  ORDERS_CSV path, bronze_path("orders") from pipeline_config.
# Outputs: bronze_orders Delta table; logged row count and ingest timestamp.

"""Bronze ingestion for orders."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pyspark.sql import SparkSession

from pipeline_config import bronze_path, orders_csv
from bronze.ingest_utils import ingest_csv_to_delta


ENTITY_NAME: str = "orders"


def ingest_orders(spark: SparkSession) -> int:
    """Ingest orders.csv into the Bronze Delta table.

    Args:
        spark: Active SparkSession.

    Returns:
        Number of rows ingested.
    """
    return ingest_csv_to_delta(
        spark, orders_csv(), bronze_path(ENTITY_NAME), ENTITY_NAME
    )


def main() -> None:
    """Run orders Bronze ingestion as a standalone job."""
    spark = SparkSession.builder.appName("bronze_ingest_orders").getOrCreate()
    ingest_orders(spark)


if __name__ == "__main__":
    main()
