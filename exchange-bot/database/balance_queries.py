from .cassandra_client import session
from datetime import datetime

def create_balance_table():
    query = """
            CREATE TABLE IF NOT EXISTS user_balance (
                user_id text PRIMARY KEY,
                balance double,
                last_updated timestamp
            )
        """
    
    session.execute(query)

def get_balance(user_id) -> float:
    query = """
            SELECT balance FROM user_balance
            WHERE user_id = %s
        """
    
    result = session.execute(query, (user_id,))
    row = result.one()
    return row.balance if row else None

def update_balance(user_id, new_balance) -> None:
    query = """
            UPDATE user_balance
            SET balance = %s, last_updated = %s
            WHERE user_id = %s            
        """
    
    session.execute(query, (new_balance, datetime.now(), user_id))

def create_user_balance(user_id, starting_balance=10000.0) -> None:
    query = """
            INSERT INTO user_balance (user_id, balance, last_updated)
            VALUES (%s, %s, %s)
        """
    
    session.execute(query, (user_id, starting_balance, datetime.now()))