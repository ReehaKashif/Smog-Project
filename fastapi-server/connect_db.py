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
    
    
    
def save_dataframe_to_db(df, table_name="octapi_data", conn_params=db_params):
    """
    Save the values of a DataFrame to a specified database table.

    Parameters:
    df (pd.DataFrame): The DataFrame to save.
    table_name (str): The name of the database table.
    conn_params (dict): Database connection parameters.

    Returns:
    None
    """
    # Establish the connection
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cursor = conn.cursor()

    # Prepare the insert query
    columns = df.columns.tolist()
    insert_query = sql.SQL(
        "INSERT INTO {} ({}) VALUES %s"
    ).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(map(sql.Identifier, columns))
    )

    # Prepare the values for insertion
    values = [tuple(x) for x in df.to_numpy()]

    try:
        execute_values(cursor, insert_query, values)
        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def check_row_count(db_params=db_params, table_name="octapi_data"):
    """
    Check the number of rows in a table.
    
    Args:
        db_params (dict): Database connection parameters (keys: dbname, user, password, host, port).
        table_name (str): Name of the table to check.

    Returns:
        int: Number of rows in the table.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Query to count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        
        # Close connection
        cursor.close()
        conn.close()
        
        return row_count
    except Exception as e:
        print(f"Error occurred while checking row count: {e}")
        return None
    
    
import numpy as np

def load_db_and_group_by_district(input_date: str, input_district: str):
    """
    Query the database to filter by date and district, calculate max values for each column, 
    and return the result as a dictionary.
    """
    try:
        # Ensure the input date is a datetime object
        input_date = pd.to_datetime(input_date).strftime('%Y-%m-%d')  # Format to YYYY-MM-DD for SQL
        
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Query the database for the specified date and district
        query = """
        SELECT * FROM octapi_data
        WHERE "date" = %s AND "District" = %s;
        """
        cursor.execute(query, (input_date, input_district))
        rows = cursor.fetchall()
        
        # Get column names from the database
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'octapi_data';")
        column_names = ['date',
                        'District',
                        'Vehicle',
                        'Industry',
                        'Residential',
                        'Misc',
                        'Construction',
                        'Agriculture',
                        'Sum_of_Sources',
                        'Vehicle_percentage',
                        'Industry_percentage',
                        'Residential_percentage',
                        'Misc_percentage',
                        'Construction_percentage',
                        'Agriculture_percentage']
        
        print(column_names)
        
        # Convert the result to a pandas DataFrame
        filtered_data = pd.DataFrame(rows, columns=column_names)
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # If no data is found, return an empty dictionary
        if filtered_data.empty:
            return {}
        
        # Calculate the maximum value for each column in the filtered data
        max_values = filtered_data.max()
        
        # Drop the 'date' and 'District' columns
        max_values = max_values.drop(['date', 'District'])
        
        # Replace NaN, inf, -inf with None so it's JSON serializable
        max_values.replace([np.inf, -np.inf, np.nan], None, inplace=True)
        
        # Convert the result to a dictionary
        result_dict = max_values.to_dict()
        
        # Replace '_percentage' with '%' in the keys
        result_dict = {key.replace('_percentage', '%'): value for key, value in result_dict.items()}
        
        return result_dict

    except Exception as e:
        # Handle exceptions and return an error message
        return {"error": str(e)}


def delete_data_by_date(input_date: str):
    """
    Deletes rows from the 'octapi_data' table that match the given date, ignoring time.
    """
    try:
        # Ensure the input date is a datetime object
        input_date = pd.to_datetime(input_date).strftime('%Y-%m-%d')  # Format to YYYY-MM-DD for SQL
        
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # SQL query to delete rows where the date matches the specified input date
        delete_query = """
        DELETE FROM octapi_data
        WHERE DATE("date") = %s;
        """
        
        # Execute the delete query
        cursor.execute(delete_query, (input_date,))
        
        # Commit the transaction
        conn.commit()
        
        # Check how many rows were deleted
        rows_deleted = cursor.rowcount
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Return the number of rows deleted
        return {"message": f"{rows_deleted} rows deleted successfully."}
    
    except Exception as e:
        # Handle exceptions and return an error message
        return {"error": str(e)}

# print(delete_data_by_date('2024-11-27'))