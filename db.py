import mysql.connector

def connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="actowiz",
        database="kia"
    )
    return conn, conn.cursor()


def create_db():
    conn, cur = connection()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dealers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100),
        city VARCHAR(100),
        name VARCHAR(255),
        address TEXT,
        phone VARCHAR(50),
        email VARCHAR(100),
        website VARCHAR(255)
    )
    """)

    conn.commit()  
    cur.close()
    conn.close()

def insert_dealers(data):
    conn, cursor = connection()

    query = """
    INSERT INTO dealers (state, city, name, address, phone, email, website)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = [
        (
            d.get("state"),
            d.get("city"),
            d.get("name"),
            d.get("address"),
            d.get("phone"),
            d.get("email"),
            d.get("website"),
        )
        for d in data
    ]

    cursor.executemany(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    print(f"{len(values)} records inserted")