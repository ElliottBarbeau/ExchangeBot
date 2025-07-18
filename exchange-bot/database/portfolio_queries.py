from .cassandra_client import session

def create_portfolio_table():
    query = """
            CREATE TABLE IF NOT EXISTS user_portfolio (
                user_id text,
                symbol text,
                amount double,
                avg_price double,
                last_updated timestamp,
                PRIMARY KEY (user_id, symbol)
            )
        """
        
    session.execute(query)

def get_portfolio(user_id, symbol):
    query = """
                SELECT amount, avg_price FROM user_portfolio
                WHERE user_id = %s AND symbol = %s
            """
            
    result = session.execute(query, (user_id, symbol))
    row = result.one()
    return row

def update_portfolio(user_id, symbol, amount, avg, now):
    query = """
                INSERT INTO user_portfolio (user_id, symbol, amount, avg_price, last_updated)
                VALUES (%s, %s, %s, %s, %s)
            """
    
    session.execute(query, (user_id, symbol, amount, avg, now))

def get_full_portfolio(user_id):
    query = "SELECT * FROM user_portfolio WHERE user_id = %s"
    result = session.execute(query, (user_id,))
    return list(result)