import psycopg2
from psycopg2 import OperationalError


# postgresql://solutiondb_user:eib6FOVoPZMc2BVguRg1etxIR81FHmDC@dpg-csnuqj8gph6c73bl4ql0-a.oregon-postgres.render.com/solutiondb
# postgresql://USER:PASSWORD@EXTERNAL_HOST:PORT/DATABASE

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="solutiondb",
            user="solutiondb_user",
            password="eib6FOVoPZMc2BVguRg1etxIR81FHmDC",
            host="dpg-csnuqj8gph6c73bl4ql0-a.oregon-postgres.render.com",
            port="5432"
        )
        print("Connection to Render PostgreSQL DB successful")
        return connection
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None

def main():
    # Connect to the database
    connection = connect_to_db()
    
    if connection:
        # Example: create a cursor and perform a simple query
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"Database version: {db_version}")
            cursor.close()
        except Exception as e:
            print(f"Query failed: {e}")
        finally:
            # Close the database connection
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
