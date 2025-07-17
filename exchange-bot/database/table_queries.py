from .cassandra_client import session

def table_exists(keyspace, table_name):
    query = """
        SELECT table_name FROM system_schema.tables
        WHERE keyspace_name = %s AND table_name = %s
    """
    result = session.execute(query, (keyspace, table_name))
    return result.one() is not None