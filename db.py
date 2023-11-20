import psycopg2

try:
    conn = psycopg2.connect(
        dbname="logdb",
        user="postgres",
        password="1234",
        host="localhost"  
    )
    cursor = conn.cursor()

    print("Connection successful")
    cursor.close()
    conn.close()

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
