"""
Financial Rules and Thresholds for Autonomous Agent

Rule-based logic for detecting financial anomalies and triggering actions.
No LLM required - uses deterministic rules for explainability.
"""

# Category spending thresholds (as percentage of monthly income)
CATEGORY_SPENDING_THRESHOLD = 0.30  # 30% of monthly income in single category

# Month-over-month spending increase threshold
SPENDING_INCREASE_THRESHOLD = 0.20  # 20% increase from last month

# Predictive spending threshold
PREDICTED_OVERSHOOT_THRESHOLD = 1.0  # 100% of income (predicted spend exceeds income)


def check_category_overspending(category_spend: float, monthly_income: float) -> bool:
    """
    Rule 1: Check if a single category spending exceeds threshold
    
    Args:
        category_spend: Total spending in a category this month
        monthly_income: User's monthly income
        
    Returns:
        True if overspending detected
    """
    if monthly_income <= 0:
        return False
    
    percentage = category_spend / monthly_income
    return percentage > CATEGORY_SPENDING_THRESHOLD


def check_spending_increase(current_month_spend: float, last_month_spend: float) -> bool:
    """
    Rule 2: Check if spending increased significantly month-over-month
    
    Args:
        current_month_spend: Total spending this month (partial or full)
        last_month_spend: Total spending last month
        
    Returns:
        True if spending increased beyond threshold
    """
    if last_month_spend <= 0:
        return False
    
    increase_ratio = (current_month_spend - last_month_spend) / last_month_spend
    return increase_ratio > SPENDING_INCREASE_THRESHOLD


def check_predictive_overshoot(
    current_spend: float, 
    days_elapsed: int, 
    days_in_month: int,
    monthly_income: float
) -> bool:
    """
    Rule 3: Predict end-of-month spending and check if it exceeds income
    
    Uses linear extrapolation: daily_average × remaining_days
    
    Args:
        current_spend: Total spending so far this month
        days_elapsed: Number of days elapsed in current month
        days_in_month: Total days in current month
        monthly_income: User's monthly income
        
    Returns:
        True if predicted spending exceeds income
    """
    if days_elapsed <= 0 or monthly_income <= 0:
        return False
    
    # Calculate daily average spending
    daily_average = current_spend / days_elapsed
    
    # Calculate remaining days
    remaining_days = days_in_month - days_elapsed
    
    # Predict total month spending
    predicted_spend = current_spend + (daily_average * remaining_days)
    
    # Check if predicted spend exceeds income
    return predicted_spend > (monthly_income * PREDICTED_OVERSHOOT_THRESHOLD)


def get_category_priority(category_spend: float, monthly_income: float) -> str:
    """
    Determine priority level for category overspending
    
    Returns:
        'high', 'medium', or 'low'
    """
    if monthly_income <= 0:
        return 'low'
    
    percentage = category_spend / monthly_income
    
    if percentage > 0.50:  # > 50% of income
        return 'high'
    elif percentage > 0.30:  # > 30% of income (threshold)
        return 'medium'
    else:
        return 'low'


def calculate_savings_suggestion(current_spend: float, monthly_income: float) -> float:
    """
    Calculate suggested savings amount
    
    Suggests saving 20% of income, adjusted for current spending
    
    Args:
        current_spend: Current monthly spending
        monthly_income: Monthly income
        
    Returns:
        Suggested monthly savings amount
    """
    target_savings_rate = 0.20  # 20% savings target
    target_savings = monthly_income * target_savings_rate
    
    # If spending is too high, suggest reducing to allow savings
    available_for_savings = monthly_income - current_spend
    
    if available_for_savings < target_savings:
        # Suggest reducing spending by the difference
        return max(0, target_savings - available_for_savings)
    else:
        return target_savings
