from db import get_db_connection

def log_auth_event(username, action, result, reason=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO auth_logs (username, action, result, reason)
            VALUES (%s, %s, %s, %s)
            """,
            (username, action, result, reason)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        # Never break auth flow because of logging
        print("AUTH LOG ERROR:", e)
