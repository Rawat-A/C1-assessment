# Purpose: Ingest customers.csv from local/DBFS into Bronze Delta (raw, no transforms).
# Inputs:  CUSTOMERS_CSV path, bronze_path("customers") from pipeline_config.
# Outputs: bronze_customers Delta table; logged row count and ingest timestamp.

"""Bronze ingestion for customers."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pyspark.sql import SparkSession

from pipeline_config import CUSTOMERS_CSV, bronze_path
from bronze.ingest_utils import ingest_csv_to_delta


ENTITY_NAME: str = "customers"
DELTA_PATH: str = bronze_path(ENTITY_NAME)


def ingest_customers(spark: SparkSession) -> int:
    """Ingest customers.csv into the Bronze Delta table.

    Args:
        spark: Active SparkSession.

    Returns:
        Number of rows ingested.
    """
    return ingest_csv_to_delta(spark, CUSTOMERS_CSV, DELTA_PATH, ENTITY_NAME)


def main() -> None:
    """Run customers Bronze ingestion as a standalone job."""
    spark = SparkSession.builder.appName("bronze_ingest_customers").getOrCreate()
    ingest_customers(spark)


if __name__ == "__main__":
    main()
