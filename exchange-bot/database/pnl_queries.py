from datetime import datetime
from .cassandra_client import session

def create_pnl_table():
    query = """
            CREATE TABLE IF NOT EXISTS user_pnl (
                user_id text PRIMARY KEY,
                pnl double,
                last_updated timestamp
            )
        """
    
    session.execute(query)

def get_pnl(user_id) -> float:
    query = """
            SELECT pnl FROM user_pnl
            WHERE user_id = %s
        """
    
    result = session.execute(query, (user_id,))
    row = result.one()
    return row.pnl if row else None

def update_pnl(user_id, new_pnl) -> None:
    query = """
            UPDATE user_pnl
            SET pnl = %s, last_updated = %s
            WHERE user_id = %s            
        """
    
    session.execute(query, (new_pnl, datetime.now(), user_id))

def create_user_pnl(user_id, starting_pnl=0) -> None:
    query = """
            INSERT INTO user_pnl (user_id, pnl, last_updated)
            VALUES (%s, %s, %s)
        """
    
    session.execute(query, (user_id, starting_pnl, datetime.now()))

def get_pnl_leaderboard(limit):
    query = "SELECT user_id, pnl FROM user_pnl"
    rows = session.execute(query)

    pnl_list = [(row.user_id, row.pnl) for row in rows]
    pnl_list.sort(key = lambda x: x[1], reverse = True)
    return pnl_list[:limit]