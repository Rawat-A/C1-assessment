# Purpose: Create Gold Delta tables by running Gold SQL against Silver temp views.
# Inputs:  Silver Delta paths; SQL files in src/gold/.
# Outputs: gold_* Delta tables; summary log.

"""Gold layer orchestration."""

import sys
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pipeline_config import HIGH_VALUE_REVENUE_THRESHOLD, gold_path, silver_path

GOLD_SQL_DIR = Path(__file__).resolve().parent

GOLD_JOBS: list[tuple[str, str, str]] = [
    ("01_sales_by_product.sql", "sales_by_product", "gold_sales_by_product"),
    ("02_revenue_by_customer.sql", "revenue_by_customer", "gold_revenue_by_customer"),
    ("03_daily_weekly_trends.sql", "daily_weekly_trends", "gold_daily_weekly_trends"),
    ("04_customer_segmentation.sql", "customer_segmentation", "gold_customer_segmentation"),
]


def _register_silver_views(spark: SparkSession) -> None:
    """Register Silver Delta tables as Spark temp views.

    Args:
        spark: Active SparkSession.
    """
    for entity in ("customers", "orders", "products"):
        df = spark.read.format("delta").load(silver_path(entity))
        df.createOrReplaceTempView(f"silver_{entity}")


def _load_sql(filename: str) -> str:
    """Read a Gold SQL file and apply config placeholders.

    Args:
        filename: SQL file name under src/gold/.

    Returns:
        SQL query string ready for spark.sql().
    """
    sql = (GOLD_SQL_DIR / filename).read_text(encoding="utf-8")
    return sql.format(high_value_threshold=HIGH_VALUE_REVENUE_THRESHOLD)


def create_gold_tables(spark: SparkSession) -> dict[str, int]:
    """Build all Gold tables from Silver data.

    Args:
        spark: Active SparkSession.

    Returns:
        Mapping of Gold table name to row count.
    """
    _register_silver_views(spark)
    counts: dict[str, int] = {}

    for sql_file, entity, table_name in GOLD_JOBS:
        query = _load_sql(sql_file)
        df: DataFrame = spark.sql(query)
        output_path = gold_path(entity)
        df.write.format("delta").mode("overwrite").save(output_path)
        row_count = df.count()
        counts[table_name] = row_count
        print(f"[Gold] {table_name}: wrote {row_count} rows -> {output_path}")

    print("=== Gold table summary ===")
    for table_name, count in counts.items():
        print(f"  {table_name}: {count} rows")
    return counts


def main() -> None:
    """Run Gold table creation."""
    spark = SparkSession.builder.appName("create_gold_tables").getOrCreate()
    create_gold_tables(spark)


if __name__ == "__main__":
    main()
