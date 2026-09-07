# Purpose: Shared helpers for accumulating Silver quality_check_result failures.
# Inputs:  DataFrame, failure conditions, reason strings.
# Outputs: DataFrame with updated quality_check_result column.

"""Silver quality-check utilities."""

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import col, concat, lit, when


def init_quality_column(df: DataFrame) -> DataFrame:
    """Initialize quality_check_result to PASS for every row.

    Args:
        df: Input DataFrame.

    Returns:
        DataFrame with quality_check_result column set to PASS.
    """
    return df.withColumn("quality_check_result", lit("PASS"))


def append_failure(df: DataFrame, condition: Column, reason: str) -> DataFrame:
    """Append a failure reason when condition is true; never remove rows.

    Args:
        df: DataFrame with quality_check_result column.
        condition: Spark Column that is True when the row fails the check.
        reason: Human-readable failure reason.

    Returns:
        DataFrame with updated quality_check_result values.
    """
    fail_expr = concat(lit("FAIL: "), lit(reason))
    return df.withColumn(
        "quality_check_result",
        when(
            condition & (col("quality_check_result") == "PASS"),
            fail_expr,
        )
        .when(
            condition & col("quality_check_result").startswith("FAIL"),
            concat(col("quality_check_result"), lit("; "), lit(reason)),
        )
        .otherwise(col("quality_check_result")),
    )


def pass_rate(df: DataFrame, condition: Column) -> float:
    """Compute percentage of rows where condition is False (check passed).

    Args:
        df: DataFrame to evaluate.
        condition: Column that is True when the row fails.

    Returns:
        Pass rate as a percentage (0-100).
    """
    total: int = df.count()
    if total == 0:
        return 100.0
    failed: int = df.filter(condition).count()
    return round((total - failed) / total * 100, 2)
