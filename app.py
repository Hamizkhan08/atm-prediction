from flask import Flask, render_template, request, send_file, jsonify
import datetime
import joblib
import pandas as pd
import io
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'atm_predictions',
    'user': 'root',
    'password': '',  # Default XAMPP MySQL password is empty
    'port': 3306
}

# Load model and feature list
model, feature_cols = joblib.load('model.pkl')

def init_database():
    """Initialize database and create table if not exists"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS atm_predictions")
        cursor.execute("USE atm_predictions")
        
        # Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            atm_id VARCHAR(50) NOT NULL,
            prediction_date DATE NOT NULL,
            transactions INT NOT NULL,
            cash_loaded DECIMAL(15,2) NOT NULL,
            prediction_result VARCHAR(100) NOT NULL,
            prediction_status ENUM('✅ Sufficiently Loaded', '⚠️ Likely to Run Out') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_atm_date (atm_id, prediction_date)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Database initialized successfully")
        
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_prediction_to_db(atm_id, date, transactions, cash_loaded, prediction_result, prediction_status):
    """Save prediction to MySQL database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO prediction_history 
        (atm_id, prediction_date, transactions, cash_loaded, prediction_result, prediction_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (atm_id, date, transactions, cash_loaded, prediction_result, prediction_status))
        connection.commit()
        return True
        
    except Error as e:
        print(f"Error saving prediction: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_prediction_history():
    """Retrieve prediction history from database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        select_query = """
        SELECT atm_id, prediction_date, transactions, cash_loaded, 
               prediction_result, prediction_status, created_at
        FROM prediction_history 
        ORDER BY created_at DESC 
        LIMIT 50
        """
        
        cursor.execute(select_query)
        history = cursor.fetchall()
        
        # Format dates for display
        for record in history:
            record['prediction_date'] = record['prediction_date'].strftime('%Y-%m-%d')
            record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return history
        
    except Error as e:
        print(f"Error retrieving history: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# app.py (Corrected version)
# In app.py

# In app.py, replace the 'home' function with this new version

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        history = get_prediction_history()
        return render_template('index.html', history=history)

    if request.method == 'POST':
        # --- 1. Collect form inputs ---
        atm_id = request.form['atm_id']
        date = request.form['date']
        cash_loaded = float(request.form['cash_loaded'])
        transactions = int(request.form['transactions'])
        day = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A')

        # --- 2. Prepare input for the REGRESSION model ---
        # The features must match exactly what the new model was trained on.
        # Notice 'Cash_Loaded' is NOT a feature for the model anymore.
        data = {col: 0 for col in feature_cols}
        data['Transactions'] = transactions
        if f'Day_of_Week_{day}' in data:
            data[f'Day_of_Week_{day}'] = 1
        
        input_df = pd.DataFrame([data])
        input_df = input_df[feature_cols] # Ensure correct column order

        # --- 3. Predict the 'Cash_Dispensed' amount ---
        predicted_dispensed = model.predict(input_df)[0]

        # --- 4. Apply business logic to determine the final status ---
        # This is where 'cash_loaded' from the form is now used.
        predicted_remaining = cash_loaded - predicted_dispensed
        
        RUN_OUT_THRESHOLD = 5000  # Define your threshold
        
        if predicted_remaining < RUN_OUT_THRESHOLD:
            status = "⚠️ Likely to Run Out"
        else:
            status = "✅ Sufficiently Loaded"

        # Create a more informative result message
        result_message = (f"ATM {atm_id} on {date}: {status}. "
                          f"(Predicted dispense: ₹{predicted_dispensed:,.0f}, "
                          f"Est. remaining: ₹{predicted_remaining:,.0f})")

        # --- 5. Save and redirect ---
        # We save the final determined status, not the raw model output
        save_prediction_to_db(atm_id, date, transactions, cash_loaded, result_message, status)
        
        flash(result_message)
        return redirect(url_for('home'))

@app.route('/api/history')
def api_history():
    """API endpoint to get history as JSON"""
    history = get_prediction_history()
    return jsonify(history)

@app.route('/download')
def download():
    """Download prediction history as CSV"""
    history = get_prediction_history()
    df = pd.DataFrame(history)
    
    if not df.empty:
        # Rename columns for CSV export
        df = df.rename(columns={
            'atm_id': 'ATM_ID',
            'prediction_date': 'Date',
            'transactions': 'Transactions',
            'cash_loaded': 'Cash_Loaded',
            'prediction_result': 'Prediction_Result',
            'prediction_status': 'Status',
            'created_at': 'Created_At'
        })
    
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'prediction_history_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear all prediction history"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM prediction_history")
        connection.commit()
        
        return jsonify({'success': True, 'message': 'History cleared successfully'})
        
    except Error as e:
        return jsonify({'success': False, 'message': f'Error clearing history: {e}'})
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Add this new function to app.py

def get_all_prediction_data():
    """Retrieve all prediction history from the database as a Pandas DataFrame."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        # Use pandas to directly read the SQL query into a DataFrame
        query = "SELECT atm_id, prediction_date, transactions, cash_loaded, prediction_status, created_at FROM prediction_history"
        df = pd.read_sql(query, connection)
        
        # Convert data types for proper analysis
        if not df.empty:
            df['prediction_date'] = pd.to_datetime(df['prediction_date'])
            df['cash_loaded'] = pd.to_numeric(df['cash_loaded'])
            df['transactions'] = pd.to_numeric(df['transactions'])
            
        return df
        
    except Error as e:
        print(f"Error retrieving full history: {e}")
        return pd.DataFrame() # Return empty DataFrame on error
    finally:
        if connection.is_connected():
            connection.close()

# Add this new route to the end of app.py, before the if __name__ == '__main__': block

@app.route('/analytics')
def analytics():
    df = get_all_prediction_data()

    if df.empty:
        return render_template('analytics.html', kpis=None, charts_data={})

    # --- 1. Calculate KPIs ---
    total_predictions = len(df)
    run_out_predictions = df[df['prediction_status'] == '⚠️ Likely to Run Out']
    run_out_count = len(run_out_predictions)
    run_out_percentage = (run_out_count / total_predictions) * 100 if total_predictions > 0 else 0
    total_cash_loaded = df['cash_loaded'].sum()

    kpis = {
        'total_predictions': total_predictions,
        'run_out_percentage': f"{run_out_percentage:.1f}%",
        'total_cash_loaded': f"₹{total_cash_loaded:,.0f}",
        'busiest_atm': df.loc[df['transactions'].idxmax()]['atm_id'] if not df.empty else 'N/A'
    }

    # --- 2. Prepare Data for Charts ---
    
    # Pie Chart: Status Distribution
    status_counts = df['prediction_status'].value_counts()
    pie_chart_data = {
        'labels': status_counts.index.tolist(),
        'data': status_counts.values.tolist()
    }

    # Bar Chart: Top 5 Riskiest ATMs
    risky_atm_counts = run_out_predictions['atm_id'].value_counts().nlargest(5)
    bar_chart_data = {
        'labels': risky_atm_counts.index.tolist(),
        'data': risky_atm_counts.values.tolist()
    }
    
    # Line Chart: Run-out predictions over time
    # Group by date and count the number of 'run out' predictions
    timeline_data_raw = run_out_predictions.groupby(pd.Grouper(key='prediction_date', freq='D')).size().sort_index()
    line_chart_data = {
        'labels': timeline_data_raw.index.strftime('%Y-%m-%d').tolist(),
        'data': timeline_data_raw.values.tolist()
    }

    charts_data = {
        'pie': pie_chart_data,
        'bar': bar_chart_data,
        'line': line_chart_data
    }

    return render_template('analytics.html', kpis=kpis, charts_data=charts_data)

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    app.run(debug=True)