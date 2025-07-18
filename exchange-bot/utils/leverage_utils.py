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
    
def calculate_liquidation_price_long(entry_price, leverage, maintenance_margin_ratio):
    return entry_price * (1 - (1 / leverage) + maintenance_margin_ratio)

def calculate_liquidation_price_short(entry_price, leverage, maintenance_margin_ratio):
    return entry_price * (1 + (1 / leverage) - maintenance_margin_ratio)