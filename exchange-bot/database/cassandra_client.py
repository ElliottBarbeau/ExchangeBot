import os

from dotenv import load_dotenv
from pathlib import Path
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ".env"

load_dotenv(BASE_DIR / ENV_FILE)

CASSANDRA_KEYSPACE = os.getenv('CASSANDRA_KEYSPACE')
CASSANDRA_PASSWORD = os.getenv('CASSANDRA_PASSWORD')
CASSANDRA_USER = os.getenv('CASSANDRA_USER')
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", 9042))
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST')

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect(CASSANDRA_KEYSPACE)
session.set_keyspace(CASSANDRA_KEYSPACE)

print(f"[Cassandra] Connected to keyspace: {CASSANDRA_KEYSPACE}")