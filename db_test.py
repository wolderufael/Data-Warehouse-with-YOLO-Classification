import psycopg2

try:
    # Connection details
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="Medical-Product",
        user="postgres",
        password="root"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")
