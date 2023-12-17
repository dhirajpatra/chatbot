import azure.functions as func
import logging
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error, pool


# load from .env
load_dotenv()

conn_string = os.getenv('CONNECTION_STRING')


# get connection with cosmosdb pgsql
def get_connection():
    postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20, conn_string)
    if (postgreSQL_pool):
        print("Connection pool created successfully")
        
        # Use getconn() to get a connection from the connection pool
        conn = postgreSQL_pool.getconn()
        cursor = conn.cursor()
        return postgreSQL_pool, conn, cursor
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Database connection failed.",
             status_code=200
        )

# this will test the connection to cosmosdb pgsql
def db_transaction(conn, cursor):
    if conn and cursor:
        print("Connection pool created successfully")
        
        # Drop previous table of same name if one exists
        cursor.execute("DROP TABLE IF EXISTS pharmacy;")
        print("Finished dropping table (if existed)")

        # Create a table
        cursor.execute("CREATE TABLE pharmacy (pharmacy_id integer, pharmacy_name text, city text, state text, zip_code integer);")
        print("Finished creating table")

        # Create a index
        cursor.execute("CREATE INDEX idx_pharmacy_id ON pharmacy(pharmacy_id);")
        print("Finished creating index")

        # Insert some data into the table
        cursor.execute("INSERT INTO pharmacy  (pharmacy_id,pharmacy_name,city,state,zip_code) VALUES (%s, %s, %s, %s,%s);", (1,"Target","Sunnyvale","California",94001))
        cursor.execute("INSERT INTO pharmacy (pharmacy_id,pharmacy_name,city,state,zip_code) VALUES (%s, %s, %s, %s,%s);", (2,"CVS","San Francisco","California",94002))
        print("Inserted 2 rows of data")
        
        # select 
        cursor.execute("SELECT * FROM pharmacy;")
        rows = cursor.fetchall()

        # Clean up
        conn.commit()
        cursor.close()
        conn.close()
        
        return rows
    
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Database transaction failed.",
             status_code=200
        )


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    # get the cosmosDB connected
    try:
        postgreSQL_pool, conn, cursor = get_connection()
    except Exception as e:
        return func.HttpResponse(
             f"This HTTP triggered function executed successfully. Database connection failed. {e}",
             status_code=200
        )
        
    # cosmosdb transaction testing
    try:
        rows = db_transaction(conn, cursor)
        results = []
        # Print all rows
        for row in rows:
            results.append("Data row = (%s, %s)" %(str(row[0]), str(row[1])))
            
    except Exception as e:
        return func.HttpResponse(
             f"This HTTP triggered function executed successfully. Database transaction failed. {e}",
             status_code=200
        )

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             f"This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response. Database also connected successfully. {conn_string} \n and Results from cosmosDB\n {str(results)}",
             status_code=200
        )