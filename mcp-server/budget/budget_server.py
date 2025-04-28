# budget_server.py

import sys

from mcp.server.fastmcp import FastMCP
from budget_manager import BudgetManager
from typing import Optional

# Initialize
budget_manager = BudgetManager()
mcp = FastMCP("Budget")

@mcp.tool()
async def add_expense(date: str, amount: float, description: str, category: str) -> str:
    """Add a new expense to the budget. Only use this when the user mentions spending money."""
    budget_manager.add_record("expense", date, amount, description, category)
    return "Expense recorded successfully."

@mcp.tool()
async def add_income(date: str, amount: float, description: str, category: str) -> str:
    """Add a new income to the budget. Only use when the user mentions receiving money."""
    budget_manager.add_record("income", date, amount, description, category)
    return "Income recorded successfully."

@mcp.tool()
async def get_expense_total(from_date: str, to_date: str) -> float:
    """Calculate the total amount spent between two dates. Use for questions about total expenses in a period."""
    return budget_manager.get_total("expense", from_date, to_date)

@mcp.tool()
async def get_income_total(from_date: str, to_date: str) -> float:
    """Calculate the total amount received between two dates. Use for questions about total income in a period."""
    return budget_manager.get_total("income", from_date, to_date)

@mcp.tool()
async def get_expenses(from_date: str, to_date: str) -> list:
    """Retrieve a detailed list of all expenses between two dates. Use if the user asks for a breakdown or list of expenses."""
    return budget_manager.query_records("expense", from_date, to_date)

@mcp.tool()
async def get_incomes(from_date: str, to_date: str) -> list:
    """Retrieve a detailed list of all incomes between two dates. Use if the user asks for a breakdown or list of incomes."""
    return budget_manager.query_records("income", from_date, to_date)

@mcp.tool()
async def get_balance(from_date: str, to_date: str) -> float:
    """Calculate net balance (income minus expenses) between two dates. Use when the user asks about profit, savings, or remaining money."""
    return budget_manager.get_balance(from_date, to_date)

@mcp.tool()
async def get_expense_total_for_category(from_date: str, to_date: str, category: str) -> float:
    """Get the total amount spent in a specific category over a time period. Use when the user asks how much they spent on a category (e.g., "food") in a period."""
    return budget_manager.get_total_for_category("expense", from_date, to_date, category)

@mcp.tool()
async def get_expense_breakdown_by_category(from_date: str, to_date: str) -> dict:
    """Get totals for each expense category over a time period. Use when the user asks for an overview of where their money went."""
    return budget_manager.get_total_breakdown_by_category("expense", from_date, to_date)

@mcp.tool()
async def get_income_total_for_category(from_date: str, to_date: str, category: str) -> float:
    """Get the total income for a specific category over a time period. Use when the user asks how much income they received from a certain source (e.g., "salary")."""
    return budget_manager.get_total_for_category("income", from_date, to_date, category)

@mcp.tool()
async def get_income_breakdown_by_category(from_date: str, to_date: str) -> dict:
    """Get totals for each income category over a time period. Use when the user asks for an overview of where their income came from."""
    return budget_manager.get_total_breakdown_by_category("income", from_date, to_date)

@mcp.tool()
async def get_allowed_categories() -> list:
    """Retrieve a list of all valid categories for expenses and incomes. Use this if you need to validate or suggest a category to the user. Only categories from this list can be used to add new expenses or incomes."""
    return budget_manager.get_allowed_categories()

@mcp.tool()
async def edit_record(
    record_id: str,
    record_type: str,
    date: str,
    amount: float,
    description: str,
    category: str
) -> str:
    """Edit an existing record by its index (use after finding it with find_records). Only use after confirming which record needs editing."""
    print(f"[DEBUG] edit_record called with:", file=sys.stderr)
    print(f"  record_id={record_id}", file=sys.stderr)
    print(f"  record_type={record_type}, date={date}, amount={amount}, description={description}, category={category}", file=sys.stderr)
    budget_manager.edit_record(record_id, record_type, date, amount, description, category)
    return "Record updated successfully."

@mcp.tool()
async def delete_record(
    record_id: str
) -> str:
    """Delete a record by its index (use after finding it with find_records). Only use after confirming which record needs deleting."""
    print(f"[DEBUG] delete_record called with record_id={record_id}", file=sys.stderr)
    budget_manager.delete_record(record_id)
    return "Record deleted successfully."


@mcp.tool()
async def find_records(
    record_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    amount: Optional[float] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
) -> list:
    """Search for matching records based on filters. Use this if the user describes a record they want to edit or delete."""
    print(f"[DEBUG] find_records called with:", file=sys.stderr)
    print(f"  record_type={record_type}, from_date={from_date}, to_date={to_date}, amount={amount}, description={description}, category={category}", file=sys.stderr)
    results = budget_manager.find_records(
        record_type=record_type,
        from_date=from_date,
        to_date=to_date,
        amount=amount,
        description=description,
        category=category
    )
    print(f"[DEBUG] find_records returning {len(results)} result(s)", file=sys.stderr)
    for r in results:
        print(f"  {r}", file=sys.stderr)
    return results


if __name__ == "__main__":
    mcp.run(transport="sse")