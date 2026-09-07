# Purpose: Ingest products.csv from local/DBFS into Bronze Delta (raw, no transforms).
# Inputs:  PRODUCTS_CSV path, bronze_path("products") from pipeline_config.
# Outputs: bronze_products Delta table; logged row count and ingest timestamp.

"""Bronze ingestion for products."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pyspark.sql import SparkSession

from pipeline_config import PRODUCTS_CSV, bronze_path
from bronze.ingest_utils import ingest_csv_to_delta


ENTITY_NAME: str = "products"
DELTA_PATH: str = bronze_path(ENTITY_NAME)


def ingest_products(spark: SparkSession) -> int:
    """Ingest products.csv into the Bronze Delta table.

    Args:
        spark: Active SparkSession.

    Returns:
        Number of rows ingested.
    """
    return ingest_csv_to_delta(spark, PRODUCTS_CSV, DELTA_PATH, ENTITY_NAME)


def main() -> None:
    """Run products Bronze ingestion as a standalone job."""
    spark = SparkSession.builder.appName("bronze_ingest_products").getOrCreate()
    ingest_products(spark)


if __name__ == "__main__":
    main()
