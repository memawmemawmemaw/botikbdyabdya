import sqlite3

def create_connection():
    """
    Создаёт соединение с базой данных.

    :return: Соединение с базой данных.
    """
    conn = sqlite3.connect("users.db")
    return conn

def create_users_table(conn):
    """
    Создаёт таблицу для хранения данных о пользователях.

    :param conn: Соединение с базой данных.
    :return: None
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            rub_balance REAL DEFAULT 0,
            usdt_balance REAL DEFAULT 0
        )
    """)
    conn.commit()

def main():
    conn = create_connection()
    create_users_table(conn)
    conn.close()

if __name__ == "__main__":
    main()

