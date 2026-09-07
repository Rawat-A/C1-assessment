# Purpose: Silver type/format validation — flag invalid types and formats; never delete rows.
# Inputs:  DataFrames with quality_check_result initialized.
# Outputs: DataFrame with type-validation failures appended to quality_check_result.

"""Silver type and format validation checks."""

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import col

from silver.quality_utils import append_failure, pass_rate


def apply_type_validation_customers(df: DataFrame) -> tuple[DataFrame, float]:
    """Validate data types on customers.

    Args:
        df: Customers DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, type-validation pass rate %).
    """
    checks: list[tuple[Column, str]] = [
        (
            col("customer_id").isNotNull() & ~col("customer_id").cast("long").isNotNull(),
            "customer_id is not a valid integer",
        ),
        (
            col("signup_date").isNotNull() & col("signup_date").cast("date").isNull(),
            "signup_date is not a valid date",
        ),
        (
            col("lifetime_value").isNotNull()
            & col("lifetime_value").cast("double").isNull(),
            "lifetime_value is not numeric",
        ),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)


def apply_type_validation_orders(df: DataFrame) -> tuple[DataFrame, float]:
    """Validate data types on orders.

    Args:
        df: Orders DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, type-validation pass rate %).
    """
    checks: list[tuple[Column, str]] = [
        (
            col("order_id").isNotNull() & ~col("order_id").cast("long").isNotNull(),
            "order_id is not a valid integer",
        ),
        (
            col("customer_id").isNotNull()
            & ~col("customer_id").cast("long").isNotNull(),
            "customer_id is not a valid integer",
        ),
        (
            col("product_id").isNotNull() & ~col("product_id").cast("long").isNotNull(),
            "product_id is not a valid integer",
        ),
        (
            col("order_date").isNotNull() & col("order_date").cast("date").isNull(),
            "order_date is not a valid date",
        ),
        (
            col("payment_date").isNotNull()
            & col("payment_date").cast("date").isNull(),
            "payment_date is not a valid date",
        ),
        (
            col("quantity").isNotNull() & col("quantity").cast("int").isNull(),
            "quantity is not a valid integer",
        ),
        (
            col("unit_price").isNotNull() & col("unit_price").cast("double").isNull(),
            "unit_price is not numeric",
        ),
        (
            col("total_amount").isNotNull()
            & col("total_amount").cast("double").isNull(),
            "total_amount is not numeric",
        ),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)


def apply_type_validation_products(df: DataFrame) -> tuple[DataFrame, float]:
    """Validate data types on products.

    Args:
        df: Products DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, type-validation pass rate %).
    """
    checks: list[tuple[Column, str]] = [
        (
            col("product_id").isNotNull() & ~col("product_id").cast("long").isNotNull(),
            "product_id is not a valid integer",
        ),
        (
            col("price").isNotNull() & col("price").cast("double").isNull(),
            "price is not numeric",
        ),
        (
            col("cost").isNotNull() & col("cost").cast("double").isNull(),
            "cost is not numeric",
        ),
        (
            col("stock_quantity").isNotNull()
            & col("stock_quantity").cast("int").isNull(),
            "stock_quantity is not a valid integer",
        ),
        (
            col("reorder_level").isNotNull()
            & col("reorder_level").cast("int").isNull(),
            "reorder_level is not a valid integer",
        ),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)
