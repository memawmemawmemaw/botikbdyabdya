import sqlite3

def create_connection():
    """
    Creates a connection to an SQLite database.

    :return: Connection to the database.
    """
    conn = sqlite3.connect("users.db")
    return conn

def add_new_columns_to_users_table(conn):
    """
    Adds new columns to the users table.

    :param conn: Database connection.
    :return: None
    """
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE users ADD COLUMN rub_balance REAL DEFAULT 0")
    cursor.execute("ALTER TABLE users ADD COLUMN usdt_balance REAL DEFAULT 0")
    conn.commit()

def migrate_balance_to_rub_balance(conn):
    """
    Migrates the data from the balance column to the rub_balance column.

    :param conn: Database connection.
    :return: None
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET rub_balance = balance")
    conn.commit()

def set_balance_to_zero(conn):
    """
    Sets the balance column to 0.

    :param conn: Database connection.
    :return: None
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = 0")
    conn.commit()
    
    
    
def get_existing_usernames(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    rows = cursor.fetchall()
    existing_usernames = [row[0] for row in rows]
    return existing_usernames    

def main():
    conn = create_connection()

    # Add new columns to the users table
    add_new_columns_to_users_table(conn)

    # Migrate data from the balance column to the rub_balance column
    migrate_balance_to_rub_balance(conn)

    # Set the balance column to 0
    set_balance_to_zero(conn)

    # Print the updated schema
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    schema = cursor.fetchall()
    print(schema)
    existing_usernames = get_existing_usernames(conn)
    print("Существующие имена пользователей:", existing_usernames)
    conn.close()

if __name__ == "__main__":
    main()