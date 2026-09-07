# Purpose: Orchestrate Bronze ingestion for customers, orders, and products.
# Inputs:  CSV paths and Bronze Delta paths from pipeline_config.
# Outputs: Three Bronze Delta tables; summary log of row counts.

"""Bronze layer orchestration."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pyspark.sql import SparkSession

from bronze.ingest_utils import ingest_csv_to_delta
from pipeline_config import bronze_path, customers_csv, orders_csv, products_csv


def ingest_all(spark: SparkSession) -> dict[str, int]:
    """Ingest all three source CSVs into Bronze Delta tables.

    Args:
        spark: Active SparkSession.

    Returns:
        Mapping of entity name to rows ingested.
    """
    counts: dict[str, int] = {
        "customers": ingest_csv_to_delta(
            spark, customers_csv(), bronze_path("customers"), "customers"
        ),
        "orders": ingest_csv_to_delta(
            spark, orders_csv(), bronze_path("orders"), "orders"
        ),
        "products": ingest_csv_to_delta(
            spark, products_csv(), bronze_path("products"), "products"
        ),
    }
    print("=== Bronze ingestion summary ===")
    for entity, count in counts.items():
        print(f"  {entity}: {count} rows")
    return counts


def main() -> None:
    """Run full Bronze ingestion."""
    spark = SparkSession.builder.appName("bronze_ingest_all").getOrCreate()
    ingest_all(spark)


if __name__ == "__main__":
    main()
