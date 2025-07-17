from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"], port=9042)
session = cluster.connect()

session.execute("""
            CREATE KEYSPACE IF NOT EXISTS exchangebot
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
        """)

session.set_keyspace('exchangebot')

print(f"[Cassandra] Connected to keyspace: exchangebot")