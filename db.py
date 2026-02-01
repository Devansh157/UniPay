import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",        # put your phpMyAdmin password if any
        database="unipay"
    )
