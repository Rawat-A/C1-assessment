# Purpose: Silver completeness checks — flag null/missing required fields; never delete rows.
# Inputs:  Bronze/Silver DataFrames for customers, orders, or products.
# Outputs: DataFrame with completeness failures appended to quality_check_result.

"""Silver completeness quality checks."""

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import col, trim

from silver.quality_utils import append_failure, pass_rate


def _is_blank(column_name: str) -> Column:
    """Return a Column that is true when the string field is null or blank."""
    return col(column_name).isNull() | (trim(col(column_name)) == "")


def apply_completeness_customers(df: DataFrame) -> tuple[DataFrame, float]:
    """Flag missing required fields on customers.

    Args:
        df: Customers DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, completeness pass rate %).
    """
    checks: list[tuple[Column, str]] = [
        (col("customer_id").isNull(), "customer_id is null"),
        (_is_blank("customer_name"), "customer_name is missing"),
        (col("email").isNull(), "email is null"),
        (_is_blank("country"), "country is missing"),
        (col("signup_date").isNull(), "signup_date is null"),
        (_is_blank("customer_segment"), "customer_segment is missing"),
        (col("lifetime_value").isNull(), "lifetime_value is null"),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)


def apply_completeness_orders(df: DataFrame) -> tuple[DataFrame, float]:
    """Flag missing required fields on orders (payment_date may be null).

    Args:
        df: Orders DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, completeness pass rate %).
    """
    checks: list[tuple[Column, str]] = [
        (col("order_id").isNull(), "order_id is null"),
        (col("customer_id").isNull(), "customer_id is null"),
        (col("order_date").isNull(), "order_date is null"),
        (col("product_id").isNull(), "product_id is null"),
        (col("quantity").isNull(), "quantity is null"),
        (col("unit_price").isNull(), "unit_price is null"),
        (col("total_amount").isNull(), "total_amount is null"),
        (_is_blank("order_status"), "order_status is missing"),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)


def apply_completeness_products(df: DataFrame) -> tuple[DataFrame, float]:
    """Flag missing required fields on products.

    Args:
        df: Products DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, completeness pass rate %).
    """
    checks: list[tuple[Column, str]] = [
        (col("product_id").isNull(), "product_id is null"),
        (_is_blank("product_name"), "product_name is missing"),
        (_is_blank("category"), "category is missing"),
        (col("price").isNull(), "price is null"),
        (col("cost").isNull(), "cost is null"),
        (col("stock_quantity").isNull(), "stock_quantity is null"),
        (col("reorder_level").isNull(), "reorder_level is null"),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)
