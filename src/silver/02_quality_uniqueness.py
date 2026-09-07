# Purpose: Silver uniqueness checks — flag duplicate primary keys; never delete rows.
# Inputs:  DataFrames with quality_check_result initialized.
# Outputs: DataFrame with uniqueness failures appended to quality_check_result.

"""Silver uniqueness quality checks."""

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import col, count
from pyspark.sql.window import Window

from silver.quality_utils import append_failure, pass_rate


def _duplicate_pk_condition(df: DataFrame, pk_column: str) -> tuple[DataFrame, Column]:
    """Mark rows whose primary key appears more than once.

    Args:
        df: Input DataFrame.
        pk_column: Primary key column name.

    Returns:
        Tuple of (DataFrame with _dup_flag helper column, duplicate condition).
    """
    window = Window.partitionBy(pk_column)
    flagged = df.withColumn("_dup_count", count("*").over(window))
    condition = col("_dup_count") > 1
    return flagged, condition


def apply_uniqueness_customers(df: DataFrame) -> tuple[DataFrame, float]:
    """Flag duplicate customer_id values.

    Args:
        df: Customers DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, uniqueness pass rate %).
    """
    flagged, condition = _duplicate_pk_condition(df, "customer_id")
    result = append_failure(flagged, condition, "duplicate customer_id")
    result = result.drop("_dup_count")
    return result, pass_rate(result, condition)


def apply_uniqueness_orders(df: DataFrame) -> tuple[DataFrame, float]:
    """Flag duplicate order_id values.

    Args:
        df: Orders DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, uniqueness pass rate %).
    """
    flagged, condition = _duplicate_pk_condition(df, "order_id")
    result = append_failure(flagged, condition, "duplicate order_id")
    result = result.drop("_dup_count")
    return result, pass_rate(result, condition)


def apply_uniqueness_products(df: DataFrame) -> tuple[DataFrame, float]:
    """Flag duplicate product_id values.

    Args:
        df: Products DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, uniqueness pass rate %).
    """
    flagged, condition = _duplicate_pk_condition(df, "product_id")
    result = append_failure(flagged, condition, "duplicate product_id")
    result = result.drop("_dup_count")
    return result, pass_rate(result, condition)
