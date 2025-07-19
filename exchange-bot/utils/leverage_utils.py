def get_maintenance_margin_ratio(leverage: float) -> float:
    if leverage <= 1:
        return 0.005
    elif leverage <= 5:
        return 0.01
    elif leverage <= 10:
        return 0.03
    elif leverage <= 20:
        return 0.05
    elif leverage <= 50:
        return 0.10
    else:
        return 0.20
    
def calculate_liquidation_price_long(entry_price, margin, amount, leverage, maintenance_margin_ratio):
    numerator = margin * (1 - maintenance_margin_ratio)
    denominator = amount * leverage
    return entry_price - (numerator / denominator)

def calculate_liquidation_price_short(entry_price, margin, amount, leverage, maintenance_margin_ratio):
    numerator = margin * (1 - maintenance_margin_ratio)
    denominator = amount * leverage
    return entry_price + (numerator / denominator)
