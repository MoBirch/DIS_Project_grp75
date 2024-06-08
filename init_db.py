import sqlite3
import pandas as pd

# Load the CSV files into DataFrames using relative paths
df_cars = pd.read_csv('cars.csv')
df_sellers = pd.read_csv('sellers.csv')  

# Fill missing values for cars
df_cars['price'] = df_cars['price'].fillna(0)
df_cars['year'] = df_cars['year'].fillna(0)
df_cars['manufacturer'] = df_cars['manufacturer'].fillna('Unknown')
df_cars['model'] = df_cars['model'].fillna('Unknown')
df_cars['fuel'] = df_cars['fuel'].fillna('Unknown')
df_cars['odometer'] = df_cars['odometer'].fillna(0)
df_cars['transmission'] = df_cars['transmission'].fillna('Unknown')
df_cars['VIN'] = df_cars['VIN'].fillna('Unknown')
df_cars['type'] = df_cars['type'].fillna('Unknown')
df_cars['paint_color'] = df_cars['paint_color'].fillna('Unknown')
df_cars['description'] = df_cars['description'].fillna('No description')
df_cars['state'] = df_cars['state'].fillna('Unknown')
df_cars['posting_date'] = df_cars['posting_date'].fillna('Unknown')

# Connect to the SQLite database
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute('DROP TABLE IF EXISTS products')
cursor.execute('DROP TABLE IF EXISTS sellers')
cursor.execute('DROP TABLE IF EXISTS buyers')

# Create the sellers table to include all columns from the CSV
cursor.execute('''
CREATE TABLE sellers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id TEXT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    password TEXT,
    address TEXT
)
''')

# Create the buyers table with additional columns
cursor.execute('''
CREATE TABLE buyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    password TEXT,
    address TEXT
)
''')

# Insert hardcoded buyer
cursor.execute('''
INSERT INTO buyers (name, email, phone, password, address) VALUES
('New User', 'new.user@example.com', '88888888', 'securepassword', '789 Maple Street')
''')

# Insert sellers from the CSV
for _, row in df_sellers.iterrows():
    cursor.execute("INSERT INTO sellers (seller_id, name, email, phone, password, address) VALUES (?, ?, ?, ?, ?, ?)",
                   (row['seller_id'], row['name'], row['email'], row['phone'], row['password'], row['address']))

# Modify the products table to include a buyer reference
cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price REAL NOT NULL,
    year INTEGER NOT NULL,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    fuel TEXT NOT NULL,
    odometer INTEGER NOT NULL,
    transmission TEXT,
    VIN TEXT,
    type TEXT,
    paint_color TEXT,
    description TEXT,
    state TEXT,
    posting_date TEXT,
    seller_id INTEGER,
    buyer_id INTEGER DEFAULT NULL,
    status TEXT DEFAULT 'AVAILABLE',
    FOREIGN KEY (seller_id) REFERENCES sellers(id),
    FOREIGN KEY (buyer_id) REFERENCES buyers(id)
)
''')

# Insert data into the products table from cars DataFrame
for _, row in df_cars.iterrows():
    cursor.execute('''
    INSERT INTO products (price, year, manufacturer, model, fuel, odometer, transmission, VIN, type, paint_color, description, state, posting_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['price'], row['year'], row['manufacturer'], row['model'], row['fuel'], row['odometer'], row['transmission'], row['VIN'], row['type'], row['paint_color'], row['description'], row['state'], row['posting_date']))

# Commit and close the connection
conn.commit()
conn.close()
