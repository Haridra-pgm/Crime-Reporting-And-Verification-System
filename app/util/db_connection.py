# db_connection.py
import mysql.connector
from mysql.connector import Error

def get_connection():
    """Establish and return the MySQL connection."""
    try:
        # Replace these with your actual database credentials
        connection = mysql.connector.connect(
            host='localhost',         # e.g., 'localhost' or IP address
            user='root',         # e.g., 'root'
            password='v@12', # your password
            database='crime',     # your database name
            port=3306  # name of the database
        )

        if connection.is_connected():
            print("Connected to the database")
            return connection

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
