import os
import sqlite3

# # Function to create the main database and tables
# def create_main_database(database_name):
#     if not os.path.exists(database_name):
#         os.makedirs(database_name)

#     main_db_path = os.path.join(database_name, 'main_database.db')

#     connection = sqlite3.connect(main_db_path)
#     c = connection.cursor()

#     # Create a table to store the list of databases
#     c.execute("""CREATE TABLE IF NOT EXISTS database_list (
#             database_name text,
#             location text,
#             creation_date text
#         )""")

#     connection.commit()
#     connection.close()

# Function to add a new database entry to the main database
def add_database_entry(database_name, location, creation_date):

    connection = sqlite3.connect('main_database.db')
    if not os.path.exists(database_name):
        os.makedirs(database_name)

    main_db_path = os.path.join(database_name, 'microplastic.db')

    c = connection.cursor()
    c.execute("INSERT INTO database_list VALUES (?, ?, ?)",
              (database_name, location, creation_date))
    connection.commit()
    connection.close()

# Function to create a new microplastics database and table
def create_microplastics_database(database_name):
    microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS microplastics (
            image_loc text,
            particle_name text,
            length real,
            width real,
            color text,
            shape text,
            magnification integer,
            note text
        )""")
    connection.commit()
    connection.close()

# Function to insert data into the microplastics table
def insert_data(database_name, image_loc, particle_name, length, width, color, shape, magnification, note):
    microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    print(microplastics_db_path)
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("INSERT INTO microplastics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (image_loc, particle_name, length, width, color, shape, magnification, note))
    print("Data added")
    connection.commit()
    connection.close()

# Function to retrieve data from the microplastics table
def get_data(database_name):
    microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("SELECT * FROM microplastics")
    data = c.fetchall()
    connection.close()
    return data

# Function to update data in the microplastics table
def update_data(database_name, particle_name, length, width, color, shape, magnification, note):
    microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("UPDATE microplastics SET length=?, width=?, color=?, shape=?, magnification=?, note=? WHERE particle_name=?",
              (length, width, color, shape, magnification, note, particle_name))
    connection.commit()
    connection.close()

# Function to delete data from the microplastics table
def delete_data(database_name, particle_name):
    microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("DELETE FROM microplastics WHERE particle_name=?", (particle_name,))
    connection.commit()
    connection.close()

# Example usage:
def main():
    main_db_name = input("Enter the name of the main database (folder name): ")
    if not main_db_name:
        print("Please provide a valid folder name.")
        return


    # Add a new database entry to the main database
    add_database_entry(main_db_name, f"{main_db_name}/microplastic.db", '2023-07-27')

    # Create the microplastics database and table
    create_microplastics_database(main_db_name)

    # Insert data into the microplastics table (replace 'None' with your actual image binary data)
    insert_data(main_db_name, None, 'Sample Particle', 10.2, 5.1, 'Blue', 'Round', 100, 'Some notes')

    # Retrieve data from the microplastics table
    data = get_data(main_db_name)
    print(data)

    # Update data in the microplastics table
    update_data(main_db_name, 'Sample Particle', 11.0, 4.8, 'Green', 'Round', 150, 'Updated notes')

    # Delete data from the microplastics table
    delete_data(main_db_name, 'Sample Particle')

if __name__ == "__main__":
    main()
