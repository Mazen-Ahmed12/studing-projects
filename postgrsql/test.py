import psycopg
import sys

# configuration : dont forget to change thosr params to your actual credentials
DB_PARAMS = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "mazen",
    "dbname": "postgres",
}


def execute_sql(sql_query, data=None, fetch_results=False):

    results = None
    try:
        with psycopg.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, data)

                if fetch_results and cur.description:
                    results = cur.fetchall()
                    print(f"[DB Action] Fetched {len(results)} rows")
                else:
                    conn.commit()
                    print("[DB Action] executed query, Rows affected: {cur.rowcount}")
    except psycopg.DatabaseError as e:
        print(f"[DB Error] A database error occured {e}")
        sys.exit(1)
    return results


if __name__ == "__main__":
    print("--- Starting Database Operations ---")

    # 1 create table
    print("\nAttempting to create 'products' table...")
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS products(
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price NUMERIC NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    execute_sql(CREATE_TABLE_SQL)

    # 2 insert mutiple items
    print("\ninserting sample products")
    INSERT_SQL = "INSERT INTO products (name, price) VALUES (%s, %s);"

    execute_sql(INSERT_SQL, data=("chair", 100))
    execute_sql(INSERT_SQL, data=("table", 200))
    execute_sql(INSERT_SQL, data=("pen", 50))

    # 3 selecct data to display
    print("\nselecting all products")
    SELECT_SQL = "SELECT name,price FROM products ORDER BY price DESC;"

    products = execute_sql(SELECT_SQL, fetch_results=True)
    print("{products}")
    if products:
        print("Products list:")
        for name, price in products:
            print(f"Name: {name}, Price: {price}")

    # 4 update data
    print("\nUpdating the price of 'chair'")
    UPDATE_SQL = "UPDATE products SET price = %s WHERE name = %s;"
    execute_sql(UPDATE_SQL, data=(150, "chair"))

    # 5 delete data
    print("\nDeleting the product 'pen'")
    DELETE_SQL = "DELETE FROM products WHERE name = %s;"

    execute_sql(DELETE_SQL, data=("pen",))

    print("\n--- Operations Complete ---")
    print("Check your TablePlus GUI to verify changes to the 'products' table.")
