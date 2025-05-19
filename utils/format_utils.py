from datetime import datetime

def format_currency(amount):
    """Format number as currency"""
    if amount is None:
        return "₱0.00"
    return f"₱{amount:,.2f}"

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if birth_date is None:
        return 0
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
