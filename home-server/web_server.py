from flask import Flask, render_template, jsonify
import config

app =  Flask(__name__)

print("Starting web server...")
print(f"Dashboard will be available at: http://localhost:{config.WEB_PORT}")

@app.route('/')
def index():
    return "<h1>IoT Dashboard</h1><p>It works!</p>"

@app.route('/api/current')
def api_current():
	data = {
		'temperature': 22.5,
        	'humidity': 65.0,
        	'light': 15000
	}
	return jsonify(data)

if __name__ == '__main__':
	app.run(
	host=config.WEB_HOST,
	port=config.WEB_PORT,
	debug=config.WEB_DEBUG
	)
