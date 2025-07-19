from .cassandra_client import session
from datetime import datetime

def create_leverage_table():
    query = """
            CREATE TABLE IF NOT EXISTS leverage_portfolio (
                user_id text,
                position_id int,
                symbol text,
                amount double,
                entry_price double,
                leverage double,
                is_long boolean,
                entry_value double,
                liquidation_price double,
                last_updated timestamp,
                PRIMARY KEY (user_id, position_id)
            )
        """
    
    session.execute(query)

def create_leverage_counter_table():
    query = """CREATE TABLE IF NOT EXISTS leverage_position_counters (
                user_id text PRIMARY KEY,
                last_id int
            )
        """
    
    session.execute(query)

def open_position(user_id, symbol, amount, entry_price, leverage, liq_price, is_long=True):
    result = session.execute(
        "SELECT last_id FROM leverage_position_counters WHERE user_id = %s", (user_id,)
    ).one()

    new_id = result.last_id + 1 if result else 1

    session.execute(
        "INSERT INTO leverage_position_counters (user_id, last_id) VALUES (%s, %s)",
        (user_id, new_id)
    )

    entry_value = abs(entry_price * amount)

    query = """
        INSERT INTO leverage_portfolio (
            user_id, position_id, symbol, amount, entry_price, leverage, 
            is_long, entry_value, liquidation_price, last_updated
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    session.execute(query, (
        user_id, new_id, symbol, amount, entry_price,
        leverage, is_long, entry_value, liq_price, datetime.now()
    ))
    return new_id

def get_leverage_portfolio(user_id):
    query = "SELECT * FROM leverage_portfolio where user_id = %s"
    result = session.execute(query, (user_id,))
    return list(result)

def close_position(user_id, position_id):
    query = "DELETE FROM leverage_portfolio WHERE user_id = %s AND position_id = %s"
    session.execute(query, (user_id, int(position_id)))

def update_position_price(user_id, position_id, amount):
    query = """
        UPDATE leverage_portfolio
        SET amount = %s, last_updated = %s
        WHERE user_id = %s AND position_id = %s
    """
    session.execute(query, (amount, datetime.utcnow(), user_id, position_id))

def get_all_user_ids_with_positions():
    query = "SELECT DISTINCT user_id FROM leverage_portfolio"
    result = session.execute(query)
    return [row.user_id for row in result]

def get_existing_position(user_id, symbol, is_long=True):
    query = """
        SELECT * FROM leverage_portfolio
        WHERE user_id = %s AND symbol = %s ALLOW FILTERING
    """
    result = session.execute(query, (user_id, symbol))
    for row in result:
        if row.is_long == is_long:
            return row
    return None

def update_position(user_id, position_id, amount, entry_price, leverage, liq_price):
    session.execute("""
        UPDATE leverage_portfolio
        SET amount = %s,
            entry_price = %s,
            leverage = %s,
            liquidation_price = %s,
            last_updated = toTimestamp(now())
        WHERE user_id = %s AND position_id = %s
    """, (amount, entry_price, leverage, liq_price, user_id, position_id))

def get_position_by_id(user_id, position_id):
    query = "SELECT * FROM leverage_portfolio WHERE user_id = %s AND position_id = %s"
    result = session.execute(query, (user_id, position_id))
    return result.one()