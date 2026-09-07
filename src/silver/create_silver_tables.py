# Purpose: Build Silver Delta tables from Bronze with all quality checks and metrics report.
# Inputs:  Bronze Delta paths; quality-check modules in src/silver/.
# Outputs: silver_* Delta tables; printed pass-rate report per check.

"""Silver layer orchestration."""

import importlib
import sys
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pipeline_config import bronze_path, silver_path
from silver.quality_utils import init_quality_column

_completeness = importlib.import_module("silver.01_quality_completeness")
_uniqueness = importlib.import_module("silver.02_quality_uniqueness")
_type_validation = importlib.import_module("silver.03_quality_type_validation")
_referential = importlib.import_module("silver.04_quality_referential_integrity")
_business_logic = importlib.import_module("silver.05_quality_business_logic")


def _read_bronze(spark: SparkSession, entity: str) -> DataFrame:
    """Load a Bronze Delta table.

    Args:
        spark: Active SparkSession.
        entity: Entity name (customers, orders, products).

    Returns:
        Bronze DataFrame.
    """
    return spark.read.format("delta").load(bronze_path(entity))


def _write_silver(df: DataFrame, entity: str) -> None:
    """Persist a Silver DataFrame to Delta.

    Args:
        df: Silver DataFrame to write.
        entity: Entity name (customers, orders, products).
    """
    path = silver_path(entity)
    df.write.format("delta").mode("overwrite").save(path)
    print(f"[Silver] Wrote {df.count()} rows -> {path}")


def _process_customers(df: DataFrame) -> tuple[DataFrame, dict[str, float]]:
    """Apply all customer quality checks.

    Args:
        df: Bronze customers DataFrame.

    Returns:
        Tuple of (Silver customers DataFrame, per-check pass rates).
    """
    df = init_quality_column(df)
    metrics: dict[str, float] = {}

    df, metrics["completeness"] = _completeness.apply_completeness_customers(df)
    df, metrics["uniqueness"] = _uniqueness.apply_uniqueness_customers(df)
    df, metrics["type_validation"] = _type_validation.apply_type_validation_customers(df)
    df, metrics["business_logic"] = _business_logic.apply_business_logic_customers(df)
    metrics["referential_integrity"] = 100.0
    return df, metrics


def _process_products(df: DataFrame) -> tuple[DataFrame, dict[str, float]]:
    """Apply all product quality checks.

    Args:
        df: Bronze products DataFrame.

    Returns:
        Tuple of (Silver products DataFrame, per-check pass rates).
    """
    df = init_quality_column(df)
    metrics: dict[str, float] = {}

    df, metrics["completeness"] = _completeness.apply_completeness_products(df)
    df, metrics["uniqueness"] = _uniqueness.apply_uniqueness_products(df)
    df, metrics["type_validation"] = _type_validation.apply_type_validation_products(df)
    df, metrics["business_logic"] = _business_logic.apply_business_logic_products(df)
    metrics["referential_integrity"] = 100.0
    return df, metrics


def _process_orders(
    df: DataFrame,
    customers: DataFrame,
    products: DataFrame,
) -> tuple[DataFrame, dict[str, float]]:
    """Apply all order quality checks including referential integrity.

    Args:
        df: Bronze orders DataFrame.
        customers: Silver customers DataFrame.
        products: Silver products DataFrame.

    Returns:
        Tuple of (Silver orders DataFrame, per-check pass rates).
    """
    df = init_quality_column(df)
    metrics: dict[str, float] = {}

    df, metrics["completeness"] = _completeness.apply_completeness_orders(df)
    df, metrics["uniqueness"] = _uniqueness.apply_uniqueness_orders(df)
    df, metrics["type_validation"] = _type_validation.apply_type_validation_orders(df)
    df, metrics["business_logic"] = _business_logic.apply_business_logic_orders(df)
    df, metrics["referential_integrity"] = _referential.apply_referential_integrity_orders(
        df, customers, products
    )
    return df, metrics


def _print_metrics_report(all_metrics: dict[str, dict[str, float]]) -> None:
    """Print per-entity quality pass rates and overall pass rate.

    Args:
        all_metrics: Nested dict of entity -> check -> pass rate %.
    """
    print("=== Silver quality metrics report (% passed per check) ===")
    for entity, checks in all_metrics.items():
        print(f"  [{entity}]")
        for check_name, rate in checks.items():
            print(f"    {check_name}: {rate}%")
        overall = checks.get("overall", 0.0)
        print(f"    overall_pass_rate: {overall}%")
    print("=== End quality report ===")


def create_silver_tables(spark: SparkSession) -> dict[str, dict[str, float]]:
    """Read Bronze, apply quality checks, write Silver, return metrics.

    Args:
        spark: Active SparkSession.

    Returns:
        Nested metrics dict keyed by entity.
    """
    bronze_customers = _read_bronze(spark, "customers")
    bronze_products = _read_bronze(spark, "products")
    bronze_orders = _read_bronze(spark, "orders")

    silver_customers, customer_metrics = _process_customers(bronze_customers)
    silver_products, product_metrics = _process_products(bronze_products)
    _write_silver(silver_customers, "customers")
    _write_silver(silver_products, "products")

    silver_orders, order_metrics = _process_orders(
        bronze_orders, silver_customers, silver_products
    )
    _write_silver(silver_orders, "orders")

    all_metrics: dict[str, dict[str, float]] = {
        "customers": customer_metrics,
        "products": product_metrics,
        "orders": order_metrics,
    }

    for entity, df_path in [
        ("customers", silver_customers),
        ("products", silver_products),
        ("orders", silver_orders),
    ]:
        total = df_path.count()
        passed = df_path.filter(col("quality_check_result") == "PASS").count()
        all_metrics[entity]["overall"] = round(passed / total * 100, 2) if total else 100.0

    _print_metrics_report(all_metrics)
    return all_metrics


def main() -> None:
    """Run Silver table creation."""
    spark = SparkSession.builder.appName("create_silver_tables").getOrCreate()
    create_silver_tables(spark)


if __name__ == "__main__":
    main()
