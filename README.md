# Sales Data Analysis Dashboard

A Docker-based data analysis application that visualizes sales data from a MySQL database.

## Overview

This project consists of two main components:
1. A MySQL database container that stores sales data
2. A Python Flask application that retrieves data from the database and generates visualizations

The application provides a web-based dashboard showing sales trends, product category performance, regional sales distribution, and top-selling products.

## Features

- Real-time sales data analysis
- Interactive web dashboard
- Multiple visualization types (bar charts, trend lines, pie charts)
- Automatic database initialization with sample data
- Containerized architecture for easy deployment

## Prerequisites

- Docker
- Docker Compose

## Getting Started

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/sales-data-analysis.git
   cd sales-data-analysis
   ```

2. Start the application:
   ```bash
   docker-compose up
   ```

3. Access the dashboard:
   Open your browser and navigate to `http://localhost:5000`

### Project Structure

```
my-dataVisual-app/
├── app.py               # Flask application and data analysis logic
├── Dockerfile           # Python application container configuration
├── docker-compose.yml   # Container orchestration configuration
└── requirements.txt     # Python dependencies
```

## How It Works

1. When started, the application automatically:
   - Initializes a MySQL database
   - Creates product and sales tables
   - Populates the database with sample data if empty
   
2. The Flask application connects to the database and:
   - Queries sales data
   - Generates visualizations using matplotlib and seaborn
   - Serves a web dashboard showing the visualizations

3. The dashboard displays:
   - Total sales by product category
   - Daily sales trends
   - Sales distribution by region
   - Top 5 products by sales volume
   - Summary statistics

## Customization

### Adding Your Own Data

To use your own sales data instead of the sample data:
1. Modify the `initialize_database()` function in `app.py`
2. Update the data initialization logic with your own dataset

### Extending Visualizations

To add new visualizations:
1. Create a new visualization function in `app.py`
2. Add a corresponding route to serve the visualization
3. Update the HTML template to include the new chart

## Troubleshooting

### Database Connection Issues

If the application cannot connect to the database:
1. Verify both containers are running: `docker ps`
2. Check MySQL logs: `docker logs sales-mysql`
3. Ensure MySQL is configured to accept connections from other containers

### Visualization Problems

If charts aren't displaying correctly:
1. Check browser console for JavaScript errors
2. Verify the Flask routes are returning proper image data
3. Ensure the database contains sufficient data for visualization

## License

This project is licensed under the MIT License - see the LICENSE file for details.
