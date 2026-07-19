import mysql.connector
from config.config import Config


def get_connection():
    """Create and return a new MySQL database connection."""
    connection = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        autocommit=False,
    )
    return connection
