"""
Autonomous Financial Agent - Core Reasoning Engine

Implements the OBSERVE → ANALYZE → PLAN → ACT loop
This is a rule-based agent (no LLM required) for explainability.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from ..db import db
from ..models import Transaction, UserPreference
from .rules import (
    check_category_overspending,
    check_spending_increase,
    check_predictive_overshoot,
    get_category_priority,
    calculate_savings_suggestion
)
from .actions import (
    create_warning_action,
    create_budget_adjustment_action,
    create_saving_suggestion_action
)


class FinancialAgent:
    """
    Autonomous Financial Agent
    
    Observes user transactions, analyzes patterns, plans interventions,
    and takes proactive actions without user commands.
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.observations = {}
        self.analysis = {}
        self.plan = []
        
    def observe(self) -> Dict:
        """
        STEP 1: OBSERVE
        Read last 30 days of transactions, income, expenses, and user preferences
        """
        # Get current date info
        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        last_month_end = current_month_start - timedelta(days=1)
        
        # Get transactions from last 30 days
        thirty_days_ago = now.date() - timedelta(days=30)
        recent_transactions = Transaction.query.filter(
            Transaction.user_id == self.user_id,
            Transaction.transaction_date >= thirty_days_ago
        ).all()
        
        # Separate current month and last month transactions
        current_month_txs = [tx for tx in recent_transactions 
                            if tx.transaction_date >= current_month_start.date()]
        last_month_txs = [tx for tx in recent_transactions
                         if last_month_start.date() <= tx.transaction_date < current_month_start.date()]
        
        # Calculate income and expenses
        current_income = sum(float(tx.amount) for tx in current_month_txs if tx.transaction_type == 'income' and tx.amount > 0)
        current_expenses = sum(abs(float(tx.amount)) for tx in current_month_txs if tx.transaction_type == 'expense' and tx.amount < 0)
        
        last_income = sum(float(tx.amount) for tx in last_month_txs if tx.transaction_type == 'income' and tx.amount > 0)
        last_expenses = sum(abs(float(tx.amount)) for tx in last_month_txs if tx.transaction_type == 'expense' and tx.amount < 0)
        
        # Estimate monthly income (use current month if available, else last month, else average)
        if current_income > 0:
            estimated_monthly_income = current_income
        elif last_income > 0:
            estimated_monthly_income = last_income
        else:
            # Calculate average from last 30 days and extrapolate
            total_income_30d = sum(float(tx.amount) for tx in recent_transactions if tx.transaction_type == 'income' and tx.amount > 0)
            estimated_monthly_income = (total_income_30d / 30) * 30  # Simple estimate
        
        # Calculate spending by category for current month
        category_spending = {}
        for tx in current_month_txs:
            if tx.transaction_type == 'expense' and tx.amount < 0:
                category = tx.category or 'Uncategorized'
                category_spending[category] = category_spending.get(category, 0) + abs(float(tx.amount))
        
        # Get user preferences (budget limits if any)
        user_prefs = UserPreference.query.filter_by(user_id=self.user_id).first()
        prefs_dict = None
        if user_prefs:
            prefs_dict = {
                'primary_goal': user_prefs.primary_goal,
                'goal_amount': float(user_prefs.goal_amount) if user_prefs.goal_amount else None,
                'interested_asset_classes': user_prefs.interested_asset_classes,
            }
        
        # Calculate days in current month
        if current_month_start.month == 12:
            next_month = current_month_start.replace(year=current_month_start.year + 1, month=1, day=1)
        else:
            next_month = current_month_start.replace(month=current_month_start.month + 1, day=1)
        days_in_month = (next_month - timedelta(days=1)).day
        
        self.observations = {
            'current_month_income': current_income,
            'current_month_expenses': current_expenses,
            'last_month_expenses': last_expenses,
            'estimated_monthly_income': estimated_monthly_income,
            'category_spending': category_spending,
            'days_elapsed_current_month': (now.date() - current_month_start.date()).days + 1,
            'days_in_current_month': days_in_month,
            'user_preferences': prefs_dict,
            'transaction_count_current': len(current_month_txs),
            'transaction_count_last': len(last_month_txs),
        }
        
        return self.observations
    
    def analyze(self) -> Dict:
        """
        STEP 2: ANALYZE
        Detect overspending, compare with last month, predict end-of-month overshoot
        """
        obs = self.observations
        
        analysis_results = {
            'category_overspending': [],
            'spending_increase_detected': False,
            'predictive_overshoot_detected': False,
            'savings_opportunity': None,
        }
        
        # Analyze category overspending
        monthly_income = obs['estimated_monthly_income']
        if monthly_income > 0:
            for category, spend in obs['category_spending'].items():
                if check_category_overspending(spend, monthly_income):
                    priority = get_category_priority(spend, monthly_income)
                    analysis_results['category_overspending'].append({
                        'category': category,
                        'spend': spend,
                        'percentage_of_income': (spend / monthly_income) * 100,
                        'priority': priority
                    })
        
        # Analyze month-over-month spending increase
        if obs['last_month_expenses'] > 0:
            if check_spending_increase(obs['current_month_expenses'], obs['last_month_expenses']):
                increase_percentage = ((obs['current_month_expenses'] - obs['last_month_expenses']) / obs['last_month_expenses']) * 100
                analysis_results['spending_increase_detected'] = True
                analysis_results['spending_increase_percentage'] = increase_percentage
        
        # Predictive analysis: check if predicted spend exceeds income
        if monthly_income > 0 and obs['days_elapsed_current_month'] > 0:
            if check_predictive_overshoot(
                obs['current_month_expenses'],
                obs['days_elapsed_current_month'],
                obs['days_in_current_month'],
                monthly_income
            ):
                analysis_results['predictive_overshoot_detected'] = True
                # Calculate predicted total
                daily_avg = obs['current_month_expenses'] / obs['days_elapsed_current_month']
                remaining_days = obs['days_in_current_month'] - obs['days_elapsed_current_month']
                analysis_results['predicted_monthly_spend'] = obs['current_month_expenses'] + (daily_avg * remaining_days)
        
        # Calculate savings opportunity
        if monthly_income > 0:
            suggested_savings = calculate_savings_suggestion(obs['current_month_expenses'], monthly_income)
            if suggested_savings > 0:
                analysis_results['savings_opportunity'] = suggested_savings
        
        self.analysis = analysis_results
        return analysis_results
    
    def plan(self) -> List[Dict]:
        """
        STEP 3: PLAN
        Decide if intervention is needed and choose action types
        """
        plan = []
        analysis = self.analysis
        obs = self.observations
        
        # Plan action for category overspending (high priority categories first)
        if analysis['category_overspending']:
            # Sort by priority (high to low)
            sorted_categories = sorted(
                analysis['category_overspending'],
                key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']],
                reverse=True
            )
            
            for cat_issue in sorted_categories[:3]:  # Top 3 categories
                category = cat_issue['category']
                spend = cat_issue['spend']
                percentage = cat_issue['percentage_of_income']
                priority = cat_issue['priority']
                
                # Calculate suggested budget (reduce by 20%)
                suggested_budget = spend * 0.80
                
                if priority == 'high':
                    action_type = 'BUDGET_ADJUSTMENT'
                    message = f"High spending alert: {category} spending is {percentage:.1f}% of your income"
                    reasoning = f"Category '{category}' spending (₹{spend:,.2f}) exceeds 30% of monthly income threshold. Consider reducing expenses in this category."
                else:
                    action_type = 'WARNING'
                    message = f"Spending alert: {category} spending is above recommended threshold"
                    reasoning = f"Category '{category}' spending ({percentage:.1f}% of income) is above the 30% threshold. Monitor this category closely."
                
                plan.append({
                    'action_type': action_type,
                    'category': category,
                    'message': message,
                    'reasoning': reasoning,
                    'suggested_budget': suggested_budget if action_type == 'BUDGET_ADJUSTMENT' else None,
                })
        
        # Plan action for spending increase
        if analysis['spending_increase_detected']:
            increase_pct = analysis.get('spending_increase_percentage', 0)
            plan.append({
                'action_type': 'WARNING',
                'message': f"Spending increased {increase_pct:.1f}% compared to last month",
                'reasoning': f"Current month expenses (₹{obs['current_month_expenses']:,.2f}) are {increase_pct:.1f}% higher than last month (₹{obs['last_month_expenses']:,.2f}). This exceeds the 20% increase threshold.",
                'category': None,
            })
        
        # Plan action for predictive overshoot
        if analysis['predictive_overshoot_detected']:
            predicted = analysis.get('predicted_monthly_spend', 0)
            plan.append({
                'action_type': 'SAVING_SUGGESTION',
                'message': f"Predicted monthly spending (₹{predicted:,.2f}) exceeds income",
                'reasoning': f"Based on current spending rate, predicted end-of-month expenses ({predicted:,.2f}) will exceed monthly income (₹{obs['estimated_monthly_income']:,.2f}). Consider reducing discretionary spending.",
                'category': None,
                'suggested_savings': analysis.get('savings_opportunity', 0),
            })
        elif analysis.get('savings_opportunity'):
            # Suggest savings even if no overshoot
            suggested = analysis['savings_opportunity']
            plan.append({
                'action_type': 'SAVING_SUGGESTION',
                'message': f"Opportunity to save ₹{suggested:,.2f} this month",
                'reasoning': f"Based on current spending patterns, you could save approximately ₹{suggested:,.2f} per month (20% of income target). Consider setting aside this amount.",
                'category': None,
                'suggested_savings': suggested,
            })
        
        self.plan = plan
        return plan
    
    def act(self) -> List:
        """
        STEP 4: ACT
        Execute planned actions - persist to database
        """
        executed_actions = []
        
        for planned_action in self.plan:
            try:
                if planned_action['action_type'] == 'WARNING':
                    action = create_warning_action(
                        user_id=self.user_id,
                        message=planned_action['message'],
                        reasoning=planned_action['reasoning'],
                        category=planned_action.get('category')
                    )
                    executed_actions.append(action)
                
                elif planned_action['action_type'] == 'BUDGET_ADJUSTMENT':
                    action = create_budget_adjustment_action(
                        user_id=self.user_id,
                        message=planned_action['message'],
                        reasoning=planned_action['reasoning'],
                        category=planned_action['category'],
                        suggested_budget=planned_action.get('suggested_budget', 0)
                    )
                    executed_actions.append(action)
                
                elif planned_action['action_type'] == 'SAVING_SUGGESTION':
                    action = create_saving_suggestion_action(
                        user_id=self.user_id,
                        message=planned_action['message'],
                        reasoning=planned_action['reasoning'],
                        suggested_savings=planned_action.get('suggested_savings', 0)
                    )
                    executed_actions.append(action)
                    
            except Exception as e:
                print(f"Error executing agent action: {str(e)}")
                continue
        
        return executed_actions
    
    def run_full_cycle(self) -> Dict:
        """
        Execute full OBSERVE → ANALYZE → PLAN → ACT cycle
        
        Returns:
            Dict with cycle results
        """
        try:
            # OBSERVE
            observations = self.observe()
            
            # Check if we have enough data
            if observations['transaction_count_current'] == 0:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough transactions to analyze',
                    'actions_taken': 0
                }
            
            # ANALYZE
            analysis = self.analyze()
            
            # PLAN
            plan = self.plan()
            
            # ACT
            actions = self.act()
            
            return {
                'status': 'success',
                'observations': {
                    'current_month_income': observations['current_month_income'],
                    'current_month_expenses': observations['current_month_expenses'],
                    'estimated_monthly_income': observations['estimated_monthly_income'],
                },
                'analysis': {
                    'category_overspending_count': len(analysis['category_overspending']),
                    'spending_increase_detected': analysis['spending_increase_detected'],
                    'predictive_overshoot_detected': analysis['predictive_overshoot_detected'],
                },
                'actions_taken': len(actions),
                'action_ids': [a.id for a in actions]
            }
            
        except Exception as e:
            print(f"Error in agent cycle: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'actions_taken': 0
            }
