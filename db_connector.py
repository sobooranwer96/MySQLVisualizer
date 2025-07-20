import mysql.connector
from mysql.connector import Error

def connect(host, username, password):
    """Establishes and returns a connection to the MySQL database."""
    connection = None
    try:
        connection = mysql.connector.connect(host=host, user=username, password=password)
        if connection.is_connected():
            print(f"Successfully connected to MySQL Database: {host}")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_all_databases(connection):
    """Fetches a list of all database names from the MySQL server."""
    databases = []
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            for (db,) in cursor:
                if db not in ['information_schema', 'mysql', 'performance_schema', 'sys']:
                    databases.append(db)
            cursor.close()
        except Error as e:
            print(f"Error fetching databases: {e}")
    return databases

def get_schema_for_database(connection, db_name):
    """
    Fetches schema information (tables and their columns) and foreign key relationships
    for a given database.
    Returns a tuple: (schema_dict, foreign_keys_list)
    schema_dict: {table_name: [{column_info}, ...], ...}
    foreign_keys_list: [{'fk_table': 'orders', 'fk_column': 'user_id', 'pk_table': 'users', 'pk_column': 'id'}, ...]
    """
    schema = {}
    foreign_keys = []

    if connection and db_name:
        try:
            cursor = connection.cursor(dictionary=True) # Return rows as dictionaries

            # Get all table names in the specified database
            cursor.execute(f"SHOW TABLES FROM `{db_name}`")
            tables = [row[f'Tables_in_{db_name}'] for row in cursor]

            # For each table, get its column details
            for table_name in tables:
                columns = []
                query_columns = f"""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_KEY, EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION;
                """
                cursor.execute(query_columns, (db_name, table_name))
                for col_info in cursor:
                    column_details = {
                        'name': col_info['COLUMN_NAME'],
                        'type': col_info['DATA_TYPE'],
                        'length': col_info['CHARACTER_MAXIMUM_LENGTH'],
                        'nullable': col_info['IS_NULLABLE'] == 'YES',
                        'key': col_info['COLUMN_KEY'],
                        'extra': col_info['EXTRA']
                    }
                    columns.append(column_details)
                schema[table_name] = columns

            # Fetch foreign key relationships for the database
            query_fks = f"""
            SELECT
                kcu.TABLE_NAME AS fk_table,
                kcu.COLUMN_NAME AS fk_column,
                kcu.REFERENCED_TABLE_NAME AS pk_table,
                kcu.REFERENCED_COLUMN_NAME AS pk_column,
                kcu.CONSTRAINT_NAME
            FROM
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu
            WHERE
                kcu.TABLE_SCHEMA = %s
                AND kcu.REFERENCED_TABLE_NAME IS NOT NULL;
            """
            cursor.execute(query_fks, (db_name,))
            for fk_info in cursor:
                foreign_keys.append({
                    'fk_table': fk_info['fk_table'],
                    'fk_column': fk_info['fk_column'],
                    'pk_table': fk_info['pk_table'],
                    'pk_column': fk_info['pk_column'],
                    'constraint_name': fk_info['CONSTRAINT_NAME']
                })
            
            cursor.close()

        except Error as e:
            print(f"Error fetching schema or foreign keys for database '{db_name}': {e}")
            schema = {}
            foreign_keys = []

    return schema, foreign_keys

