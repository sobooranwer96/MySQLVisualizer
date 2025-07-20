import mysql.connector
from mysql.connector import Error

# Replace these with your MySQL connection details.
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root', # Your MySQL password
}

TEST_DB_NAME = "hotel_booking_test_db"

def create_database_and_schema():
    """
    Connects to MySQL, drops the test database if it exists,
    creates a new test database, and populates it with tables
    including PK, FK, and UNIQUE constraints.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()

        if connection.is_connected():
            print(f"Successfully connected to MySQL server for database creation.")

            # Drop database if it already exists
            try:
                cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DB_NAME}`")
                print(f"Dropped existing database: `{TEST_DB_NAME}` (if it existed).")
            except Error as e:
                print(f"Error dropping database (might not exist): {e}")

            # Create the new database
            cursor.execute(f"CREATE DATABASE `{TEST_DB_NAME}`")
            print(f"Created new database: `{TEST_DB_NAME}`.")

            # Switch to the new database
            cursor.execute(f"USE `{TEST_DB_NAME}`")
            print(f"Switched to database: `{TEST_DB_NAME}`.")

            # Create Tables with Keys

            # Table: Guests
            create_guests_table_query = """
            CREATE TABLE Guests (
                guest_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE, -- UNIQUE KEY
                phone_number VARCHAR(20),
                address VARCHAR(255)
            );
            """
            cursor.execute(create_guests_table_query)
            print("Table 'Guests' created.")

            # Table: Rooms
            create_rooms_table_query = """
            CREATE TABLE Rooms (
                room_id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(10) NOT NULL UNIQUE, -- UNIQUE KEY
                room_type VARCHAR(50) NOT NULL,
                price_per_night DECIMAL(10, 2) NOT NULL,
                capacity INT NOT NULL
            );
            """
            cursor.execute(create_rooms_table_query)
            print("Table 'Rooms' created.")

            # New Table: Staff
            create_staff_table_query = """
            CREATE TABLE Staff (
                staff_id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(20) NOT NULL UNIQUE, -- UNIQUE KEY
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                role VARCHAR(50) NOT NULL
            );
            """
            cursor.execute(create_staff_table_query)
            print("Table 'Staff' created.")

            # Table: Bookings 
            create_bookings_table_query = f"""
            CREATE TABLE Bookings (
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                guest_id INT NOT NULL,
                room_id INT NOT NULL,
                staff_id INT,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
                FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
                FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
            );
            """
            cursor.execute(create_bookings_table_query)
            print("Table 'Bookings' created.")

            print(f"\nDatabase '{TEST_DB_NAME}' created successfully!")

    except Error as e:
        print(f"Error during database creation: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    create_database_and_schema()
