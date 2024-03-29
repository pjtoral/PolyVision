import os
import sqlite3

# Function to create the main database and tables
def create_main_database(database_name):
    if not os.path.exists(database_name):
        os.makedirs(database_name)

    main_db_path = os.path.join(database_name, 'main_database.db')

    connection = sqlite3.connect(main_db_path)
    c = connection.cursor()

    # Create a table to store the list of databases
    c.execute("""CREATE TABLE IF NOT EXISTS database_list (
            database_name text,
            location text,
            creation_date text
        )""")

    connection.commit()
    connection.close()


def create_retraining_database(database_name):
    if not os.path.exists(database_name):
        os.makedirs(database_name)

    main_db_path = os.path.join(database_name, 'retrain_images.db')

    connection = sqlite3.connect(main_db_path)
    c = connection.cursor()

    # Create a table to store the list of databases
    c.execute("""CREATE TABLE IF NOT EXISTS database_list (
            image_name text,
            is_microplastic bool,
            bounding_box text
        )""")

    connection.commit()
    connection.close()


def retrain_data(database_name, image_name, is_microplastic, bounding_box):
    microplastics_db_path = os.path.join(database_name, 'retrain_images.db')
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    is_microplastic_send = int(is_microplastic) 
 
    c.execute("INSERT INTO database_list (image_name, is_microplastic, bounding_box) VALUES (?, ?, ?)",
              (image_name, is_microplastic_send, bounding_box))
    
    connection.commit()
    connection.close()

def count_rows_in_retraining_database(database_name):
    main_db_path = os.path.join(database_name, 'retrain_images.db')

    connection = sqlite3.connect(main_db_path)
    c = connection.cursor()

    # Execute a query to count the number of rows in the database_list table
    c.execute("SELECT COUNT(*) FROM database_list")

    # Fetch the count
    count = c.fetchone()[0]

    connection.close()

    return count

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
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("INSERT INTO microplastics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (image_loc, particle_name, length, width, color, shape, magnification, note))
    connection.commit()
    connection.close()

# Function to retrieve data from the microplastics table
def get_data(database_name):

    if ".db" not in database_name:
        microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    else:
        microplastics_db_path = database_name
        
    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("SELECT * FROM microplastics")
    data = c.fetchall()
    connection.close()
    return data

def get_image_data(database_name, particle_name):
    microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    connection = sqlite3.connect(microplastics_db_path)
    particle_name = particle_name.split('.')[0]
    c = connection.cursor()
    c.execute("SELECT * FROM microplastics WHERE particle_name = ?", (particle_name,))
    image_data = c.fetchall()
    connection.close()
    return image_data

def update_all_data(database_name, particle_name, length, width, color, shape, magnification, note):

    if ".db" not in database_name:
        microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    else:
        microplastics_db_path = database_name

    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("UPDATE microplastics SET length=?, width=?, color=?, shape=?, magnification=?, note=? WHERE particle_name=?",
              (length, width, color, shape, magnification, note, particle_name))
    connection.commit()
    connection.close()

def update_table_data(database_name, particle_name, length, width, color, shape, row_id):

    if ".db" not in database_name:
        microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    else:
        microplastics_db_path = database_name

    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("UPDATE microplastics SET particle_name=?, length=?, width=?, color=?, shape=? WHERE ROWID=?",
              (particle_name, length, width, color, shape, row_id))
    connection.commit()
    connection.close()

def clear_table_data(database_name):
    
    if ".db" not in database_name:
        microplastics_db_path = os.path.join(database_name, 'microplastic.db')
    else:
        microplastics_db_path = database_name

    connection = sqlite3.connect(microplastics_db_path)
    c = connection.cursor()
    c.execute("UPDATE microplastics SET 'particle_name' = '', 'length' = '', 'width' = '', 'color' = '', 'shape' = ''")
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


def main():
    create_retraining_database("E:/THESIS/PolyVision/UI")
    count_rows_in_retraining_database("E:/THESIS/PolyVision/UI")

if __name__ == "__main__":
    main()
