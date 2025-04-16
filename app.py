import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from flask import Flask, render_template, jsonify, send_file
import io
from datetime import datetime, timedelta
import random

# Initialize Flask app
app = Flask(__name__)

# Function to connect to MySQL and fetch data
def get_db_connection():
    # Using environment variables for configuration
    retries = 5
    while retries > 0:
        try:
            connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'mysql'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', 'admin123'),
                database=os.getenv('MYSQL_DATABASE', 'sales_db')
            )
            return connection
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            retries -= 1
            if retries > 0:
                print(f"Retrying in 5 seconds... ({retries} attempts left)")
                time.sleep(5)
            else:
                raise
    return None

# Function to initialize the database
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(50),
            price DECIMAL(10, 2)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            product_id INT,
            quantity INT,
            total_price DECIMAL(10, 2),
            sale_date DATETIME,
            region VARCHAR(50),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    if product_count == 0:

        # Insert sample products
        products = [
            ("Laptop", "Electronics", 999.99),
            ("Smartphone", "Electronics", 699.99),
            ("Headphones", "Electronics", 199.99),
            ("T-shirt", "Clothing", 19.99),
            ("Jeans", "Clothing", 49.99),
            ("Sneakers", "Footwear", 89.99),
            ("Coffee Maker", "Appliances", 129.99),
            ("Blender", "Appliances", 79.99),
            ("Watch", "Accessories", 149.99),
            ("Backpack", "Accessories", 59.99)
        ]
        
        cursor.executemany("INSERT INTO products (name, category, price) VALUES (%s, %s, %s)", products)
        
        # Generate sample sales data
        regions = ["North", "South", "East", "West", "Central"]
        
        # Generate sales for the past 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        sales_data = []
        
        for _ in range(1000):  # Generate 1000 sales records
            product_id = random.randint(1, len(products))
            quantity = random.randint(1, 5)
            product_price = products[product_id-1][2]
            total_price = quantity * product_price
            
            # Random date within the past 30 days
            days_ago = random.randint(0, 30)
            sale_date = end_date - timedelta(days=days_ago)
            
            # Random region
            region = random.choice(regions)
            
            sales_data.append((product_id, quantity, total_price, sale_date, region))
        
        cursor.executemany(
            "INSERT INTO sales (product_id, quantity, total_price, sale_date, region) VALUES (%s, %s, %s, %s, %s)",
            sales_data
        )
        
        conn.commit()
    
    cursor.close()
    conn.close()

# Fetch all sales data with product information
def get_sales_data():
    conn = get_db_connection()
    query = '''
    SELECT s.id, p.name, p.category, s.quantity, s.total_price, s.sale_date, s.region
    FROM sales s
    JOIN products p ON s.product_id = p.id
    ORDER BY s.sale_date
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Create various visualizations
def generate_category_sales_chart():
    df = get_sales_data()
    plt.figure(figsize=(10, 6))
    category_sales = df.groupby('category')['total_price'].sum().sort_values(ascending=False)
    
    ax = sns.barplot(x=category_sales.index, y=category_sales.values)
    plt.title('Total Sales by Product Category')
    plt.xlabel('Category')
    plt.ylabel('Total Sales ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save to bytesIO
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()
    return img_bytes

def generate_daily_sales_chart():
    df = get_sales_data()
    df['date'] = pd.to_datetime(df['sale_date']).dt.date
    daily_sales = df.groupby('date')['total_price'].sum().reset_index()
    
    plt.figure(figsize=(12, 6))
    plt.plot(daily_sales['date'], daily_sales['total_price'], marker='o', linestyle='-')
    plt.title('Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Total Sales ($)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()
    return img_bytes

def generate_region_chart():
    df = get_sales_data()
    plt.figure(figsize=(9, 6))
    region_sales = df.groupby('region')['total_price'].sum()
    
    plt.pie(region_sales, labels=region_sales.index, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Sales Distribution by Region')
    plt.tight_layout()
    
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()
    return img_bytes

def generate_top_products_chart():
    df = get_sales_data()
    plt.figure(figsize=(10, 6))
    product_sales = df.groupby('name')['total_price'].sum().sort_values(ascending=False).head(5)
    
    ax = sns.barplot(x=product_sales.index, y=product_sales.values)
    plt.title('Top 5 Products by Sales')
    plt.xlabel('Product')
    plt.ylabel('Total Sales ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()
    return img_bytes

# Flask routes
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sales Data Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            h1 { color: #333; text-align: center; }
            .dashboard { display: flex; flex-wrap: wrap; justify-content: center; }
            .chart-container { margin: 15px; background: white; padding: 15px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            img { max-width: 100%; height: auto; }
            .summary { margin: 20px auto; max-width: 800px; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <h1>Sales Data Analysis Dashboard</h1>
        
        <div class="summary">
            <h2>Sales Summary</h2>
            <div id="summary-data">Loading summary data...</div>
        </div>
        
        <div class="dashboard">
            <div class="chart-container">
                <h2>Category Sales</h2>
                <img src="/chart/category" alt="Category Sales Chart">
            </div>
            
            <div class="chart-container">
                <h2>Daily Sales Trend</h2>
                <img src="/chart/daily" alt="Daily Sales Trend">
            </div>
            
            <div class="chart-container">
                <h2>Sales by Region</h2>
                <img src="/chart/region" alt="Regional Sales Chart">
            </div>
            
            <div class="chart-container">
                <h2>Top 5 Products</h2>
                <img src="/chart/top_products" alt="Top Products Chart">
            </div>
        </div>
        
        <script>
            // Fetch summary data
            fetch('/api/summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('summary-data').innerHTML = `
                        <p><strong>Total Sales:</strong> $${data.total_sales.toFixed(2)}</p>
                        <p><strong>Average Order Value:</strong> $${data.avg_order.toFixed(2)}</p>
                        <p><strong>Total Number of Orders:</strong> ${data.total_orders}</p>
                        <p><strong>Best Selling Category:</strong> ${data.best_category}</p>
                        <p><strong>Best Selling Product:</strong> ${data.best_product}</p>
                    `;
                });
        </script>
    </body>
    </html>
    '''

@app.route('/chart/category')
def category_chart():
    img_bytes = generate_category_sales_chart()
    return send_file(img_bytes, mimetype='image/png')

@app.route('/chart/daily')
def daily_chart():
    img_bytes = generate_daily_sales_chart()
    return send_file(img_bytes, mimetype='image/png')

@app.route('/chart/region')
def region_chart():
    img_bytes = generate_region_chart()
    return send_file(img_bytes, mimetype='image/png')

@app.route('/chart/top_products')
def top_products_chart():
    img_bytes = generate_top_products_chart()
    return send_file(img_bytes, mimetype='image/png')

@app.route('/api/summary')
def get_summary():
    df = get_sales_data()
    
    total_sales = df['total_price'].sum()
    total_orders = len(df)
    avg_order = total_sales / total_orders if total_orders > 0 else 0
    
    best_category = df.groupby('category')['total_price'].sum().idxmax()
    best_product = df.groupby('name')['total_price'].sum().idxmax()
    
    return jsonify({
        'total_sales': total_sales,
        'avg_order': avg_order,
        'total_orders': total_orders,
        'best_category': best_category,
        'best_product': best_product
    })

if __name__ == '__main__':
    # Initialize database when app starts
    initialize_database()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

            
