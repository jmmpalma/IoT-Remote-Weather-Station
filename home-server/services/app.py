from flask import Flask, render_template, jsonify
import psycopg2
import config
import re
import os

# This tells Flask the template folder is in the parent directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

def get_db_connection():
    return psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Get last 48 weather entries (Ambient Temp/Hum)
    cur.execute("SELECT timestamp, temperature, humidity FROM weather_data ORDER BY timestamp DESC LIMIT 48")
    weather_rows = cur.fetchall()
    
    # 2. Get last 20 system logs
    cur.execute("SELECT timestamp, event_type, message FROM system_logs ORDER BY timestamp DESC LIMIT 20")
    log_rows = cur.fetchall()
    
    cur.close()
    conn.close()

    # Process logs and extract CPU Temp for graphing
    logs_formatted = []
    cpu_history = []
    
    for r in log_rows:
        time_str = r[0].strftime('%H:%M:%S')
        logs_formatted.append({"time": time_str, "event": r[1], "msg": r[2]})
        
        # Extract CPU temp using Regex if it's a HEARTBEAT log
        if "CPU:" in r[2]:
            match = re.search(r"CPU: (\d+\.\d+)C", r[2])
            if match:
                cpu_history.append({"time": time_str, "val": float(match.group(1))})

    # Prepare final JSON
    return jsonify({
        "weather": [{"time": r[0].strftime('%d/%m %H:%M'), "temp": r[1], "hum": r[2]} for r in reversed(weather_rows)],
        "logs": logs_formatted,
        "cpu": list(reversed(cpu_history))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)