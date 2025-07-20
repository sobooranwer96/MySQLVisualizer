MySQL Visualizer
This is a basic Python application that visualizes your MySQL database schema, displaying tables, their columns (including Primary and Foreign Keys), and drawing relationships between them.

Table of Contents
Prerequisites

Environment Setup

Database Setup

Running the Application

1. Prerequisites
Before you begin, ensure you have the following installed on your system:

Python 3.x: (Python 3.8 or newer).

MySQL Server: A running MySQL database server.

MySQL Client Tools: command-line client and optionally MySQL Workbench

2. Environment Setup
Install Python Libraries:
Install the necessary Python library for connecting to MySQL.

pip install mysql-connector-python

3. Database Setup
To test the visualization of foreign key relationships, you'll need a database with tables that have these relationships. A utility script create_test_db.py is provided for this purpose.

Open create_test_db.py:
Edit the create_test_db.py file in your project directory.

Update MySQL Credentials:
Locate the DB_CONFIG dictionary and replace 'your_mysql_root_password' with your actual MySQL root password (or the password of a user with privileges to create and drop databases).

Run the database creation script:

python create_test_db.py

This script will:

Connect to your MySQL server.

Drop the hotel_booking_test_db database if it already exists (for a clean slate).

Create a new hotel_booking_test_db database.

Create Guests, Rooms, Staff, and Bookings tables with Primary, Unique, and Foreign Key constraints.

You should see confirmation messages in your terminal.

4. Running the Application
Now that your environment and database are set up, you can run the MySQL Visualizer.

Run the GUI application:

python visualize_mysql.py

Interact with the Application:

A Tkinter window will appear.

Enter your MySQL Host (e.g., localhost), Username (e.g., root), and Password (your MySQL password).

Click the "Connect" button.

If successful, the screen will switch to the visualization canvas, and the "Select Database" dropdown will be populated.

Select hotel_booking_test_db from the dropdown.

Click the "Load Schema" button.

You should now see the Guests, Rooms, Staff, and Bookings tables drawn on the canvas, with columns, key indicators ([PK], [FK], [UN]), and lines connecting the foreign key relationships!