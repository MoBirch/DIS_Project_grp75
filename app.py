from flask import Flask, request, render_template, jsonify
import sqlite3
import re

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row # This will allow us to access columns by name
    return conn

@app.route('/')
def index(): 
    return render_template('search.html') # Render the search template

@app.route('/sellers')
def sellers():
    conn = get_db_connection()
    sellers = conn.execute('SELECT * FROM sellers').fetchall()
    conn.close()
    return render_template('sellers.html', sellers=sellers)


@app.route('/buyers')
def buyers():
    conn = get_db_connection()
    buyers = conn.execute('SELECT * FROM buyers').fetchall()
    conn.close()
    return render_template('buyers.html', buyers=buyers)

# the "main page" where you can search for cars
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query') # Get the query string from the URL
    price_range = request.args.get('price') # Get the price range from the URL
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    where_clauses = [] # This will store the WHERE clauses for the SQL query
    params = [] # This will store the values for the WHERE clauses
    # fetch on price range to minimize the number of results to begin with
    if price_range: 
        if '-' in price_range: # If the price range is specified as "min-max"
            min_price, max_price = map(float, price_range.split('-')) # Split the range into min and max
            where_clauses.append("price BETWEEN ? AND ?") # Add the WHERE clause for the price range
            params.extend([min_price, max_price]) # Add the min and max prices to the params list
        else:
            min_price = float(price_range) # If only one price is specified, use it as the minimum price
            where_clauses.append("price >= ?") # Add the WHERE clause for the price
            params.append(min_price) # Add the min price to the params list

    where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1' # Combine the WHERE clauses with AND
    cursor.execute(f"SELECT * FROM products WHERE {where_clause}", params) # Execute the SQL query
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # filter results based on query using regex
    if query:
        regex = re.compile(query, re.IGNORECASE) # Compile the regex pattern
        filtered_results = [row for row in results if regex.search(row['manufacturer']) or regex.search(row['model'])] # Filter the results
    else:
        filtered_results = results
    
    products = [dict(row) for row in filtered_results] # Convert the results to a list of dictionaries

    return jsonify(products) 

#route to see detailed view of car including description
@app.route('/car/<int:id>')
def car_detail(id):
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone() # Fetch the car with the specified ID
    conn.close()
    if car is None: # If the car is not found, return a 404 error
        return render_template('404.html'), 404
    return render_template('car_detail.html', car=car)

# Buying a car (updating sales table)
@app.route('/buy/<int:id>', methods=['POST'])
def buy(id):
    buyer_id = 1234  # Hardcoded buyer_id for simplicity

    try:
        conn = get_db_connection()
        cursor = conn.cursor() 
        cursor.execute("UPDATE products SET buyer_id = ?, status = 'SOLD' WHERE id = ?", (buyer_id, id)) # Update the product status to SOLD
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'id': id}) 
    except sqlite3.Error as e:
        return jsonify({'status': 'error', 'message': str(e)})


# Deleting a car (updating product status) (available in view sales)
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (id,)) # Delete the product with the specified ID
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success', 'id': id})

#route to view sales
@app.route('/view-sales')
def view_sales():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE status = 'SOLD'") # Fetch all the sold cars
    cars = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_sales.html', sales=cars)  # Pass the sales data to the template

if __name__ == '__main__':
    app.run(debug=True)
