import pandas as pd
import datetime
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.errors import UniqueViolation
from psycopg2 import sql


# Database connection parameters (replace with actual credentials)
db_params = {
    'dbname': 'smog_db',
    'user': 'smog_dev',
    'password': 'kcSzXTAg1RSXktipRM9gN9cD32pGFN2k',
    'host': 'dpg-csnu6npu0jms73913fh0-a.oregon-postgres.render.com',
    'port': '5432'
}

def insert_pivot_data(pivot_data, db_params=db_params, table_name="combined_hourly_data"):
    """
    Insert pivot data into the database. Handle duplicate key violations gracefully.

    Args:
        pivot_data: DataFrame containing the data to insert.
        db_params: Dictionary containing the database connection parameters.
        table_name: Name of the database table.

    Returns:
        A dictionary with the status and either inserted values or existing values in case of duplicates.
    """
    try:
        # Establish the connection
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()

        # Get column names from the DataFrame
        columns = list(pivot_data.columns)

        # Create the INSERT query with quoted column names
        insert_query = sql.SQL(
            "INSERT INTO {} ({}) VALUES %s"
        ).format(
            sql.Identifier(table_name),
            sql.SQL(", ").join([sql.Identifier(col) for col in columns])
        )

        # Prepare data for insertion
        values = [tuple(row) for row in pivot_data.to_numpy()]

        # Execute batch insertion
        execute_values(cursor, insert_query, values)

        # Close the connection
        cursor.close()
        conn.close()

        print("Data inserted successfully.")
        return values

    except UniqueViolation as e:
        # Handle duplicate key violation
        conn.rollback()  # Roll back the transaction
        print("Duplicate data detected. Retrieving existing data.")

        # Fetch existing data for the conflicting date and hour
        conflicting_date = pivot_data['date'].iloc[0]
        conflicting_hour = pivot_data['hour'].iloc[0]

        query = sql.SQL("""
            SELECT * FROM {}
            WHERE date = %s AND hour = %s
        """).format(sql.Identifier(table_name))

        cursor.execute(query, (conflicting_date, conflicting_hour))
        existing_data = cursor.fetchall()

        # Format the existing data for the date and hour columns
        formatted_existing_data = []
        for row in existing_data:
            date = row[0].strftime('%m/%d/%Y')  # Format date as MM/DD/YYYY
            hour = row[1].strftime('%H:%M')     # Format time as HH:MM
            formatted_row = (date, hour) + row[2:]  # Add the formatted date and hour to the rest of the row
            formatted_existing_data.append(formatted_row)

        # Close the connection
        cursor.close()
        conn.close()

        # Return the formatted existing data
        return formatted_existing_data

    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}


def get_last_24_hours(district):
    # Establish the connection
    conn = psycopg2.connect(**db_params)
    conn.autocommit = True
    cursor = conn.cursor()

    query = sql.SQL("""
        SELECT date, hour, {}
        FROM combined_hourly_data
        WHERE {} IS NOT NULL
        ORDER BY date DESC, hour DESC
        LIMIT 24
    """).format(sql.Identifier(district), sql.Identifier(district))

    cursor.execute(query)
    rows = cursor.fetchall()

    # Extract only the hourly values into a single array
    hourly_values = [row[2] for row in rows]
    
    # Close the connection
    cursor.close()
    conn.close()

    return hourly_values



def fetch_hourly_aqi_from_db(district: str, date: str, db_params=db_params):
    """
    Query the database for hourly AQI data for a specified district and date.
    
    Args:
        district: Name of the district (column name for AQI data).
        date: Date in MM/DD/YYYY format.
        db_params: Dictionary containing database connection parameters.
    
    Returns:
        Tuple of hours and AQI values.
    """
    try:
        # Convert date string to date object
        query_date = datetime.datetime.strptime(date, "%m/%d/%Y").date()
        
        # Establish the connection
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()

        # Construct the SQL query
        query = sql.SQL("""
            SELECT hour, {}
            FROM combined_hourly_data
            WHERE date = %s
            ORDER BY hour
        """).format(sql.Identifier(district))  # Dynamically select the column based on district
        
        # Execute the query with date as the parameter
        cursor.execute(query, (query_date,))
        rows = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        conn.close()

        # Format hours as strings like "0:00", "1:00", etc., and extract AQI values
        if rows:
            hours = [f"{row[0].hour}:00" for row in rows]  # Format hours as strings
            aqi_values = [row[1] for row in rows]           # Extract AQI values for the district column
            return hours, aqi_values
        else:
            return None, None

    except Exception as e:
        raise Exception(f"Database query failed: {e}")