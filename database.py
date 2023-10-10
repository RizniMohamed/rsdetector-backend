import psycopg2
from psycopg2 import pool
import bcrypt

class Database:
    __connection_pool = None

    @staticmethod
    def initialize(minconn, maxconn, **kwargs):
        Database.__connection_pool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, **kwargs)

    @staticmethod
    def get_connection():
        return Database.__connection_pool.getconn()

    @staticmethod
    def return_connection(connection):
        Database.__connection_pool.putconn(connection)

    @staticmethod
    def close_all_connections():
        Database.__connection_pool.closeall()

# Initialize the connection pool
Database.initialize(1, 10, 
                    dbname='rsdetector', 
                    user='postgres', 
                    password='postgres', 
                    host='127.0.0.1', 
                    port='5432')

def get_text(label):
    """Retrieve text information for a given label."""
    query = "SELECT * FROM sign_information WHERE id='{}';".format(label)
    connection = Database.get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[2]
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Return the connection back to the pool
        Database.return_connection(connection)
        
def store_image_metadata(upload_timestamp, processing_time, file_size, file_type):
    # Assuming you have a database connection pool
    connection = Database.get_connection()

    try:
        with connection.cursor() as cursor:
            # Prepare SQL query
            query = """
                INSERT INTO image_metadata (
                    upload_timestamp,
                    processing_time,
                    file_size,
                    file_type
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """
            # Execute SQL query
            cursor.execute(query, (upload_timestamp, processing_time, file_size, file_type))
            
            # Commit the transaction
            connection.commit()
            
            # Get the generated id
            image_id = cursor.fetchone()[0]

            return image_id

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, rollback the transaction on error
        connection.rollback()

    finally:
        # Return the connection back to the pool
        Database.return_connection(connection)

def update_processing_time(image_id, processing_time):
    # Assuming you have a database connection pool
    connection = Database.get_connection()

    try:
        with connection.cursor() as cursor:
            # Prepare SQL query
            query = """
                UPDATE image_metadata
                SET processing_time = %s
                WHERE id = %s;
            """
            # Execute SQL query
            cursor.execute(query, (processing_time, image_id))
            
            # Commit the transaction
            connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, rollback the transaction on error
        connection.rollback()

    finally:
        # Return the connection back to the pool
        Database.return_connection(connection)

def store_processing_results(image_id, result):
    
    connection = Database.get_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                    INSERT INTO public.processing_results (
                        image_id, detected_label, recognized_label, 
                        detection_confidence_score, cropped_image,recognition_confidence_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
            cursor.execute(query, (
                    image_id, result['detected_label'], result['recognized_label'],
                    result['detection_confidence_score'], result['cropped_image'], result['recognition_confidence_score']
                ))
            
            # Commit the transaction
            connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, rollback the transaction on error
        connection.rollback()

    finally:
        # Return the connection back to the pool
        Database.return_connection(connection)
    

def store_error_in_db(error_message, timestamp, file_name, function_name):
    
    connection = Database.get_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO public.error_logs (error_message, error_timestamp, file_name, function_name)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(query, (error_message, timestamp, file_name, function_name))
            
            # Commit the transaction
            connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, rollback the transaction on error
        connection.rollback()

    finally:
        # Return the connection back to the pool
        Database.return_connection(connection)
    

def store_user(password, email):
    
    # Get a database connection from the connection pool
    connection = Database.get_connection()

    try:
        with connection.cursor() as cursor:
            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Prepare SQL query
            query = """
                INSERT INTO public.users (
                    password,
                    email
                )
                VALUES (%s, %s)
            """

            # Execute SQL query
            cursor.execute(query, (hashed_password, email))

            # Commit the transaction
            connection.commit()
            
            return 0

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, rollback the transaction on error
        connection.rollback()
        if "duplicate" in str(e):
            return 1
        else:
            return 2

    finally:
        # Return the connection back to the pool
        Database.return_connection(connection)
        
    
def get_user(email):
    # Get a database connection from the connection pool
    connection = Database.get_connection()

    try:
        with connection.cursor() as cursor:
            # Prepare SQL query
            query = """
                SELECT * FROM public.users
                WHERE email = %s;
            """
            # Execute SQL query
            cursor.execute(query, (email,))
            # Fetch one record
            user = cursor.fetchone()
            return user

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Return the connection back to the pool
        Database.return_connection(connection)
