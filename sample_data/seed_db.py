#Run once before running project to create sqlite3 database

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")

SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT,
    signup_date TEXT
);

CREATE TABLE products (
    product_id  INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT,
    price       REAL NOT NULL
);

CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL,
    order_date      TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_tem_id    INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL,
    FOREIGN KEY (order_id)  REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
"""

CUSTOMERS = [
    (1, "Ananya Rao", "Chennai", "2023-01-12"),

    (2, "Vikram Singh", "Bengaluru", "2023-02-03"), 

    (3, "Priya Menon", "Chennai", "2023-02-20"),

    (4, "Rahul Verma", "Mumbai", "2023-03-05"),

    (5, "Sneha Iyer", "Chennai", "2023-03-18"),

    (6, "Arjun Nair", "Hyderabad", "2023-04-02"),

    (7, "Divya Krishnan", "Bengaluru", "2023-04-22"),

    (8, "Karthik Raja", "Chennai", "2023-05-10"),

    (9, "Meera Pillai", "Kochi", "2023-05-30"),

    (10, "Suresh Kumar", "Mumbai", "2023-06-14"),
]

PRODUCTS = [
    (1, "Wireless Mouse", "Electronics", 799.0),

    (2, "Mechanical Keyboard", "Electronics", 3499.0),

    (3, "USB-C Hub", "Electronics", 1299.0),

    (4, "Office Chair", "Furniture", 6999.0),

    (5, "Standing Desk", "Furniture", 15999.0),

    (6, "Notebook Set", "Stationery", 249.0),

    (7, "Fountain Pen", "Stationery", 599.0),

    (8, "Desk Lamp", "Furniture", 1499.0),

    (9, "Webcam HD", "Electronics", 2199.0),

    (10, "Noise Cancelling Headphones", "Electronics", 7999.0),
]

ORDERS = [
    (1,1,"2024-01-05"), (2,2, "2024-01-08"), (3,1,"2024-01-15"),
    (4,3,"2024-01-20"), (5,4,"2024-02-02"), (6,5,"2024-02-10"),
    (7,2,"2024-02-14"), (8,6,"2024-02-18"), (9,7,"2024-03-01"),
    (10,3,"2024-03-05"), (11,8,"2024-03-11"), (12,9,"2024-03-15"),
    (13,1,"2024-03-20"), (14,10,"2024-03-25"), (15,4,"2024-04-02"),
    (16,5,"2024-04-08"), (17,6,"2024-04-12"), (18,2,"2024-04-18"),
    (19,7,"2024-04-22"), (20,9,"2024-04-29"),
]

ORDER_ITEMS = [
    (1,1,1,2), (2,1,2,1), (3,2,4,1), (4,3,3,3),
    (5,4,5,1), (6,5,6,5), (7,6,8,2), (8,7,9,1),
    (9,8,10,1), (10,9,1,4), (11,10,2,2), (12,11,7,3),
    (13,12,3,1), (14,13,4,1), (15,14,10,1), (16,15,6,2),
    (17,16,5,1), (18,17,8,1), (19,18,9,2), (20,19,1,1),
    (21,20,2,1), (22,5,3,2), (23,9,10,1), (24,12,9,1),
    (25,15,1,3), (26,3,6,4), (27,7,2,1), (28,11,4,1),
    (29,16,8,2), (30,20,5,1),
]

def seed() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", CUSTOMERS)
    cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", PRODUCTS)
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?)", ORDERS)
    cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", ORDER_ITEMS)
    conn.commit()
    conn.close()
    print(f"Seeded database at {DB_PATH}")

if __name__ == "__main__":
    seed()
